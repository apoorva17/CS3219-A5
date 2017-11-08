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
        }])
        
    def getSubCollectionSizePerVenues(self, subCollectionName, venues, year):
       """Returns the number of distinct number of elements named 'subCollectionName' per year.
	   for the different venues in a precise year
       """
       venuesRgx=[]
       for v in venues:
           venuesRgx.append(re.compile("^{}$".format(v), re.IGNORECASE))
		   
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
