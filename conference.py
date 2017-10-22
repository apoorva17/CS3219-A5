import argparse
import xml.etree.ElementTree as etree
import json
import time
from glob import glob

CONST_FILE_NAME = 'Data/data_paper.json'

#get the number of author for paper where the venue is sepcified
#attributs: nbAuth: number of authors to return
#           venue: name of the venue
def getTopAuthByVenue(nbAuth, venue, lines):
    authors = {}
    for line in lines:
        j = json.loads(line)

        if j['venue'].upper() == venue.upper():
            authorList = j['authors']
            for a in authorList:
                if (len(a['ids'])>0):
                    if (a['ids'][0] in authors):
                        authors[a['ids'][0]][0] += 1
                    else:
                        authors[a['ids'][0]] = []
                        authors[a['ids'][0]].append(1)
                        authors[a['ids'][0]].append(a['name'])

    authors = sorted(authors.items(), key=lambda t:t[1], reverse=True)
    listAuthors = []
    for i in range(0, nbAuth):
        listAuthors.append(authors[i])
    return listAuthors


#return a collection of paper associated to the number of time it is cited
#attributs : numPaper: number of papers to return
#          : venue: name of the conference
def getPaperMostCited(numPaper, venue, lines):
    papers = {}
    for line in lines:
        j = json.loads(line)

        if j['venue'].upper() == venue.upper():
            idPaper = j['id']
            citations = j['inCitations']
            papers[idPaper] = []
            papers[idPaper].append(len(citations))
            papers[idPaper].append(j['title'])

    papers = sorted(papers.items(), key = lambda t:t[1], reverse=True)
    listPapers = []
    for i in range(0, numPaper):
        listPapers.append(papers[i])
    return listPapers

#get the amount of publication per year for a specified venue
#attributs : venue: name of the conference
def getAmountPublicationPerYear(venue, lines):
    year_publication = {}

    for line in lines:
        j = json.loads(line)

        if j['venue'].upper() == venue.upper():
            if j['year'] != "":
                if (j['year'] in year_publication):
                    year_publication[j['year']] += 1
                else:
                    year_publication[j['year']] = 1

    year_publication = sorted(year_publication.items(), key = lambda t:t[0], reverse = True)
    return year_publication


def getPaperName(citations, lines):
    for line in lines:
        j = json.loads(line)
        if j['id'] in citations.keys():
            citations[j['id']][0] = j['title']
            citations[j['id']].append(j['authors'])

    value_to_remove = ""
    result = {key: value for key, value in citations.items() if value[0] != value_to_remove}

    return result

#get the tree of citation corresponding to a base paper
#attributes: paper_name: name of the base paper
#            tree_level: level of the tree (up to 2 in the assignment)
def getCitationTreeByPaper(paper_name, tree_level, lines):
    collection_paper = []
    dict_citations = {}
    for line in lines:
        j = json.loads(line)
        if j['title'].upper() == paper_name.upper():
            citations = j['inCitations']
            for id_paper in citations:
                dict_citations[id_paper] = []
                dict_citations[id_paper].append("")
            if (tree_level == 0):
                return getPaperName(dict_citations, lines)
            else:
                paper_names = getPaperName(dict_citations, lines)
                rsltt_dict = {}
                for k in paper_name:
                    rsltt_dict[paper_name] = getCitationTreeByPaper(paper_name, tree_level-1, lines)
                return rsltt_dict
            break


def main():
    f = open(CONST_FILE_NAME, 'r', encoding="utf8")
    lines = f.readlines()
    f.close()

    #print(getTopAuthByVenue(5, "arXiv", lines))

    #print(getPaperMostCited(5, "arXiv", lines))

    #print(getAmountPublicationPerYear("arXiv", lines))

    #print(getCitationTreeByPaper("Low-density parity check codes over GF(q)", 0, lines))
    fin = time.clock()

if __name__ == '__main__':
    main()