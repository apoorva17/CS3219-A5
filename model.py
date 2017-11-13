import os
import re
import json
from pymongo import MongoClient


class Model(object):
    """Handles all data querying for CIR application.

    NOTE: To use any of the original JSON-based queries, you must first
    run model.loadJsonFile()
    """

    def __init__(self):
        self.json_path = 'config/mongo/data.json'
        self.client = MongoClient(os.environ['MONGO_HOST'], port=int(os.environ['MONGO_PORT']))
        self.db = self.client.cir

    def loadJsonFile(self):
        f = open(self.json_path, 'r', encoding="utf8")
        self.json_file = [json.loads(l) for l in f.readlines()]
        f.close()

    # -------------------------------------------------------------------------
    #   NoSQL-based Queries
    # -------------------------------------------------------------------------

    def getSubCollectionSizePerYear(self, subCollectionName, venue, yearMin, yearMax):
        """Returns the number of distinct number of elements named 'subCollectionName' per year.

        subCollectionName: example "authors" or "outCitations"
        venue: restrict to venue with name (case insensitive)
        yearMin, yearMax: restrict to year range
        """

        venueRegx = re.compile("^{}$".format(venue), re.IGNORECASE)
        return self.db.papers.aggregate([{
            "$match": {"$and": [
                {"venue": venueRegx},
                {"year": {"$gte": yearMin, "$lte": yearMax}},
            ]},
        }, {
            "$unwind": "$" + subCollectionName,
        }, {
            "$group": {
                "_id": {"yearGroup": "$year"},
                "uniqueItems": {"$addToSet": "$" + subCollectionName},
            },
        }, {
            "$project": {
                "label": "$_id.yearGroup",
                "value": {"$size": "$uniqueItems"},
            }
        }, {
            "$sort": {"label": 1},
        }], allowDiskUse=True)

    def getSubCollectionSizePerVenues(self, subCollectionName, venues, year):
        """Returns the number of distinct number of elements named 'subCollectionName' per
        venue for a precise year.
        """
        venuesRgx = [re.compile("^{}$".format(v), re.IGNORECASE) for v in venues]
        return self.db.papers.aggregate([{
            "$match": {"$and": [
                {"venue": {"$in": venuesRgx}},
                {"year": year},
            ]},
        }, {
            "$unwind": "$" + subCollectionName,
        }, {
            "$group": {
                "_id": {"venueGroup": "$venue"},
                "uniqueItems": {"$addToSet": "$" + subCollectionName},
            },
        }, {
            "$project": {
                "label": "$_id.venueGroup",
                "value": {"$size": "$uniqueItems"},
            }
        }, {
            "$sort": {"label": 1},
        }])

    def getPaperMostCited(self, numPaper, venue):
        """Returns a collection of papers associated with the number of times it is cited.

        numPaper: number of papers to return
        venue: name of the conference
        """
        regx = re.compile("^{}$".format(venue), re.IGNORECASE)
        return self.db.papers.aggregate([{
            "$match": {"venue": regx},
        }, {
            "$project": {
                "title": 1,
                "citationsCount": {"$size": "$inCitations"},
            },
        }, {
            "$sort": {"citationsCount": -1},
        }, {
            "$limit": numPaper,
        }])

    def getRelationAuthor(self, author, group):
        cursor = self.db.papers.aggregate([{
            "$match": {"authors": {"$elemMatch": {"name": author}}},
        }, {
            "$unwind": "$authors",
        }, {
            "$group": {
                "_id": {"Group": "$" + group},
                "uniqueItems": {"$addToSet": "$authors.name"},
            },
        }])

        nodes = []
        edges = []
        n = 1
        nodes.append((0, author, author, "#0000FF"))
        for j in cursor:
            if (group != "year"):
              title = list(j['_id']['Group'])
              if len(title) > 15:
                title = title[:15]
                title[14] = '.'
                title[13] = '.'
                title[12] = '.'
              titlec = "".join(title)
            else:
             titlec = j['_id']['Group']
            nodes.append((n,titlec, j['_id']['Group'], "#FF0000"))
            edges.append((0, n))
            g = n
            n += 1
            for name in j['uniqueItems']:
                if author not in name:
                    nodes.append((n, name, name, '#00FF00'))
                    edges.append((g, n))
                    n += 1
        return nodes, edges

    def getCitationGraph(self, title, max_depth):
        colors = {0: '#FF0000', 1: '#00FF00', 2: '#FFFF00', 3: '#A2A2A2'}

        # Get root paper ID
        title = title.replace("(", "\(").replace(")", "\)")
        titleRegx = re.compile("^{}$".format(title), re.IGNORECASE)
        root_paper = self.db.papers.find_one({"title": titleRegx})
        if root_paper is None:
            return [], []
        root_id = root_paper['id']

        nodes = set([root_id])
        edges = set()
        node_level = {root_id: 0}

        for i in range(max_depth):
            new_nodes = []

            for j in self.db.papers.find():
                if j['id'] in nodes:
                    for citation in j['inCitations']:
                        new_nodes.append(citation)
                        edges.add((citation, j['id']))

            for n in new_nodes:
                if n not in node_level.keys():
                    node_level[n] = i + 1
                nodes.add(n)

        # Get paper names
        named_nodes = []
        for j in self.db.papers.find():
            if j['id'] in nodes:
                authors = []
                title = list(j['title'])
                title_complete = list(j['title'])
                for a in j['authors']:
                    if(len(authors) != len(j['authors']) - 1):
                        authors.append(a['name'] + ", ")
                    else:
                        authors.append(a['name'])
                if len(title) > 15:
                    title = title[:15]
                    title[14] = '.'
                    title[13] = '.'
                    title[12] = '.'
                named_nodes.append((j['id'], "".join(title), "".join(title_complete) + "<br />" + "".join(authors), colors.get(node_level[j['id']], "#0000FF")))

        return named_nodes, edges

    def getTopNElements(self, n, elementType, filterKeys, filterValues):
        """Returns the top N items of type 'elementType' subject to the filters provided.

        n:            number of items to return
        elementType:  if 'inCitations' or 'outCitations', result will be document name
                      if 'authors', result will be author name
        filterKeys:   if 'authors', filter will be based on author name
                      otherwise, filterKey should directly be the name of a key
        filterValues: values for the filterKeys
        """
        aggregation_pipeline = []

        # First expand sub-collections we want to filter or search.
        if elementType == "authors" or "author" in filterKeys:
            aggregation_pipeline.append({
                "$unwind": "$authors",
            })
        if elementType == "inCitations":
            aggregation_pipeline.append({
                "$unwind": "$inCitations",
            })
        if elementType == "outCitations":
            aggregation_pipeline.append({
                "$unwind": "$outCitations",
            })

        # Add all filters as case-insensitive regex.
        for key, value in zip(filterKeys, filterValues):
            if key == "author":
                key = "authors.name"
            if key in ("year"):
                aggregation_pipeline.append({
                    "$match": {key: int(value)},
                })
            else:
                aggregation_pipeline.append({
                    "$match": {key: re.compile("^{}$".format(value), re.IGNORECASE)},
                })

        # Find top items of elementType.
        aggregation_pipeline.extend([{
            "$group": {
                "_id": {"elementTypeGroup": "$" + elementType},
                "numOccurences": {"$sum": 1},
            },
        }, {
            "$sort": {"numOccurences": -1},
        }, {
            "$limit": n,
        }, {
            "$project": {
                "label": "$_id.elementTypeGroup",
                "value": "$numOccurences",
            }
        }])

        # Find more friendly names for the labels.
        if elementType == "authors":
            aggregation_pipeline.append({
                "$project": {
                    "label": "$label.name",
                    "value": 1,
                },
            })
        if elementType in ["inCitations", "outCitations"]:
            aggregation_pipeline.extend([{
                "$lookup": {
                    "from": "papers",
                    "localField": "label",
                    "foreignField": "id",
                    "as": "document",
                },
            }, {
                "$project": {
                    "label": {"$ifNull": ["$document.title", "$label"]},
                    "value": 1,
                }
            }])

        return self.db.papers.aggregate(aggregation_pipeline, allowDiskUse=True)

    # -------------------------------------------------------------------------
    #   Original JSON-based Queries
    # -------------------------------------------------------------------------

    def getTopAuthByVenue(self, nbAuth, venue):
        """Get the number of authors for paper where the venue is specified.

        nbAuth: number of authors to return
        venue: name of the venue
        """
        authors = {}
        for j in self.json_file:
            if j['venue'].upper() == venue.upper():
                authorList = j['authors']
                for a in authorList:
                    if (len(a['ids']) > 0):
                        if (a['ids'][0] in authors):
                            authors[a['ids'][0]][0] += 1
                        else:
                            authors[a['ids'][0]] = []
                            authors[a['ids'][0]].append(1)
                            authors[a['ids'][0]].append(a['name'])

        authors = sorted(authors.items(), key=lambda t: t[1], reverse=True)
        listAuthors = []
        for i in range(0, nbAuth):
            listAuthors.append(authors[i])
        return listAuthors

    def getAmountPublicationPerYear(self, venue):
        """Get the amount of publication per year for a specified venue.

        venue: name of the conference
        """
        year_publication = {}

        for j in self.json_file:
            if j['venue'].upper() == venue.upper():
                if j['year'] != "":
                    if (j['year'] in year_publication):
                        year_publication[j['year']] += 1
                    else:
                        year_publication[j['year']] = 1

        year_publication = sorted(year_publication.items(), key=lambda t: t[0])
        return year_publication

    def getCitationTreeByPaper(self, paper_name, tree_level):
        colors = {0: '#FF0000', 1: '#00FF00', 2: '#FFFF00'}

        # Get paper ID
        for j in self.json_file:
            if j['title'].upper() == paper_name.upper():
                paper_id = j['id']
                break

        nodes = set([paper_id])

        node_level = {}
        node_level[paper_id] = 0
        edges = set()

        for i in range(tree_level):

            new_nodes = []

            for j in self.json_file:
                if j['id'] in nodes:
                    for citation in j['inCitations']:
                        new_nodes.append(citation)
                        edges.add((citation, j['id']))

            for n in new_nodes:
                if (n not in node_level.keys()):
                    node_level[n] = i + 1
                nodes.add(n)

        print(node_level)
        # Get paper names
        named_nodes = []
        for j in self.json_file:
            if j['id'] in nodes:
                authors = []
                title = list(j['title'])
                title_complete = list(j['title'])
                for a in j['authors']:
                    if(len(authors) != len(j['authors']) - 1):
                        authors.append(a['name'] + ", ")
                    else:
                        authors.append(a['name'])
                if len(title) > 15:
                    title = title[:15]
                    title[14] = '.'
                    title[13] = '.'
                    title[12] = '.'
                named_nodes.append((j['id'], "".join(title), "".join(title_complete), ''.join(authors), colors[node_level[j['id']]]))

        return named_nodes, edges

    def getAuthorID(self, name):
        for j in self.json_file:
            list_dict_auth = j['authors']
            for dict in list_dict_auth:
                if dict["name"] == name and dict["ids"] != []:
                    return dict["ids"][0]
        return ""

    def getNumberOfTimeCitedPerYear(self, yearMin, yearMax, author):
        """Get the # times that author was cited between yearMin & yearMax.

        Example of execution: getNumberOfTimeCitedPerYear(2000, 2016,"Yoshua Bengio",json_file)

        yearMin: year minimum
        yeaMax: year maximum
        author: author
        lines: data
        """
        dict_citation = {}

        for i in range(yearMin, yearMax + 1):
            dict_citation[i] = 0

        authorID = self.getAuthorID(author, self.json_file)
        print(authorID)
        if (authorID != ""):
            for j in self.json_file:
                list_dict_auth = j['authors']
                for dict in list_dict_auth:
                    list_id = dict["ids"]
                    for id in list_id:
                        if id == authorID:
                            if j['year'] in dict_citation.keys():
                                dict_citation[j['year']] += 1

        dict_citation = sorted(dict_citation.items(), key=lambda t: t[0])
        return dict_citation
