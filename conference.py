import json
from flask import Flask
from jinja2 import Environment, FileSystemLoader, select_autoescape

CONST_FILE_NAME = 'Data/data_paper.json'


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
def getPaperMostCited(numPaper, venue, json_file):
    papers = {}
    for j in json_file:
        if j['venue'].upper() == venue.upper():
            idPaper = j['id']
            citations = j['inCitations']
            papers[idPaper] = []
            papers[idPaper].append(len(citations))
            papers[idPaper].append(j['title'])

    papers = sorted(papers.items(), key=lambda t: t[1], reverse=True)
    listPapers = []
    for i in range(0, numPaper):
        listPapers.append(papers[i])
    return listPapers


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

    year_publication = sorted(year_publication.items(), key=lambda t: t[0], reverse=True)
    return year_publication


def getPaperName(citations, json_file):
    for j in json_file:
        if j['id'] in citations.keys():
            citations[j['id']][0] = j['title']
            citations[j['id']].append(j['authors'])

    value_to_remove = ""
    result = {key: value for key, value in citations.items() if value[0] != value_to_remove}

    return result


# Get the tree of citation corresponding to a base paper
# attributes: paper_name: name of the base paper
#             tree_level: level of the tree (up to 2 in the assignment)
def getCitationTreeByPaper(paper_name, tree_level, json_file):
    collection_paper = []
    dict_citations = {}
    for j in json_file:
        if j['title'].upper() == paper_name.upper():
            citations = j['inCitations']
            for id_paper in citations:
                dict_citations[id_paper] = []
                dict_citations[id_paper].append("")
            if (tree_level == 1):
                return getPaperName(dict_citations, json_file)
            else:
                paper_names = getPaperName(dict_citations, json_file)
                rsltt_dict = {}
                for k in paper_name:
                    rsltt_dict[paper_name] = getCitationTreeByPaper(paper_name, tree_level - 1, json_file)
                return rsltt_dict
            break

def getAuthorID(name, json_file):
    for j in json_file:
        list_dict_auth = j['authors']
        for dict in list_dict_auth:
            if dict["name"] == name and dict["ids"] != []:
                return dict["ids"][0]
    return ""

# example of execution: getNumberOfTimeCitedPerYear(2000, 2016,"Yoshua Bengio",json_file)
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
    return 'CS3219 Assignment 4<br /><br />Question <a href="/1">1</a> <a href="/2">2</a> <a href="/3">3</a> <a href="/4">4</a>'


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
    f = open(CONST_FILE_NAME, 'r', encoding="utf8")
    lines = f.readlines()
    f.close()

    json_file = []
    for line in lines:
        j = json.loads(line)
        json_file.append(j)

    data = getPaperMostCited(5, "arXiv", json_file)
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

    data = getCitationTreeByPaper("Low-density parity check codes over GF(q)", 2, json_file)
    template = env.get_template('templates/question4.html')
    return template.render(data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
