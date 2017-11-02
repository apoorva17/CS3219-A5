import os
import re
import json
from flask import Flask
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pymongo import MongoClient

CONST_FILE_NAME = 'config/mongo/data.json'

client = MongoClient(os.environ['MONGO_HOST'], port=int(os.environ['MONGO_PORT']))
db = client.cir


# Get the number of author for paper where the venue is sepcified
# attributs: nbAuth: number of authors to return
#            venue: name of the venue
def getTopAuthByVenue(nbAuth, venue, json_file):
    authors = {}
    for j in json_file:
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


# Return a collection of paper associated to the number of time it is cited
# attributs : numPaper: number of papers to return
#           : venue: name of the conference
def getPaperMostCited(numPaper, venue):
    regx = re.compile("^{}$".format(venue), re.IGNORECASE)
    return db.papers.aggregate([{
        "$match": {"venue": regx},
    }, {
        "$project": {
            "title": 1,
            "citations_count": {"$size": {"$ifNull": ["$inCitations", []]}},
        }
    }, {
        "$sort": {"citations_count": -1},
    }, {
        "$limit": numPaper,
    }])


# Get the amount of publication per year for a specified venue
# attributs : venue: name of the conference
def getAmountPublicationPerYear(venue, json_file):
    year_publication = {}

    for j in json_file:
        if j['venue'].upper() == venue.upper():
            if j['year'] != "":
                if (j['year'] in year_publication):
                    year_publication[j['year']] += 1
                else:
                    year_publication[j['year']] = 1

    year_publication = sorted(year_publication.items(), key=lambda t: t[0])
    return year_publication


def getCitationTreeByPaper(paper_name, tree_level, json_file):
    colors = {0: '#FF0000', 1: '#00FF00', 2: '#FFFF00'}

    # Get paper ID
    for j in json_file:
        if j['title'].upper() == paper_name.upper():
            paper_id = j['id']
            break

    nodes = set([paper_id])

    node_level = {}
    node_level[paper_id] = 0
    edges = set()

    for i in range(tree_level):

        new_nodes = []

        for j in json_file:
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
    for j in json_file:
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


def getAuthorID(name, json_file):
    for j in json_file:
        list_dict_auth = j['authors']
        for dict in list_dict_auth:
            if dict["name"] == name and dict["ids"] != []:
                return dict["ids"][0]
    return ""


# Example of execution: getNumberOfTimeCitedPerYear(2000, 2016,"Yoshua Bengio",json_file)
# attributs: yearMin: year minimum
#           yeaMax: year maximum
#           author: author
#           lines: data
def getNumberOfTimeCitedPerYear(yearMin, yearMax, author, json_file):
    dict_citation = {}

    for i in range(yearMin, yearMax + 1):
        dict_citation[i] = 0

    authorID = getAuthorID(author, json_file)
    print(authorID)
    if (authorID != ""):
        for j in json_file:
            list_dict_auth = j['authors']
            for dict in list_dict_auth:
                list_id = dict["ids"]
                for id in list_id:
                    if id == authorID:
                        if j['year'] in dict_citation.keys():
                            dict_citation[j['year']] += 1

    dict_citation = sorted(dict_citation.items(), key=lambda t: t[0])
    return dict_citation


# Web Server
# --------------------------------------------
app = Flask(__name__)
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml'])
)


@app.route('/')
def hello_world():
    return 'CS3219 Assignment 4<br /><br />Question <a href="/1">1</a> <a href="/2">2</a> <a href="/3">3</a> <a href="/4">4</a> <a href="/5">5</a>'


@app.route('/1')
def question_1():
    f = open(CONST_FILE_NAME, 'r', encoding="utf8")
    lines = f.readlines()
    f.close()

    json_file = []
    for line in lines:
        j = json.loads(line)
        json_file.append(j)

    data = getTopAuthByVenue(10, "arXiv", json_file)
    template = env.get_template('templates/question1.html')
    return template.render(data=data)


@app.route('/2')
def question_2():
    data = getPaperMostCited(5, "arXiv")
    template = env.get_template('templates/question2.html')
    return template.render(data=data)


@app.route('/3')
def question_3():
    f = open(CONST_FILE_NAME, 'r', encoding="utf8")
    lines = f.readlines()
    f.close()

    json_file = []
    for line in lines:
        j = json.loads(line)
        json_file.append(j)

    data = getAmountPublicationPerYear("ICSE", json_file)
    template = env.get_template('templates/question3.html')
    return template.render(data=data)


@app.route('/4')
def question_4():
    f = open(CONST_FILE_NAME, 'r', encoding="utf8")
    lines = f.readlines()
    f.close()

    json_file = []
    for line in lines:
        j = json.loads(line)
        json_file.append(j)

    nodes, edges = getCitationTreeByPaper("Low-density parity check codes over GF(q)", 2, json_file)
    print(nodes)
    template = env.get_template('templates/question4.html')
    return template.render(nodes=nodes, edges=edges)


@app.route('/5')
def question_5():
    f = open(CONST_FILE_NAME, 'r', encoding="utf8")
    lines = f.readlines()
    f.close()

    json_file = []
    for line in lines:
        j = json.loads(line)
        json_file.append(j)

    data = getNumberOfTimeCitedPerYear(2000, 2016, "Yoshua Bengio", json_file)
    template = env.get_template('templates/question5.html')
    return template.render(data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
