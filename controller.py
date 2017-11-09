from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask import url_for

class Controller(object):
    """Handles all interaction between Model & View."""

    def __init__(self, model):
        self.jinja_env = Environment(
            loader=FileSystemLoader('./'),
            autoescape=select_autoescape(['html'])
        )
        self.model = model

    def index(self):
        view = self.jinja_env.get_template('views/index.html')
        return view.render()

    # -------------------------------------------------------------------------
    #   A5 Questions
    # -------------------------------------------------------------------------

    def trend1(self, subCollectionName, venue, yearMin, yearMax):
        data = self.model.getSubCollectionSizePerYear(
            subCollectionName=subCollectionName,
            venue=venue,
            yearMin=yearMin,
            yearMax=yearMax,
        )
        view = self.jinja_env.get_template('views/line_chart.html')
        return view.render(
            title="Number of {} per year ({}, {}-{})".format(
                subCollectionName, venue, yearMin, yearMax),
            xLabel="Year",
            yLabel="Number of {}".format(subCollectionName),
            data=data,
        )

    def trend2(self, subCollectionName, venues, year):
        data = self.model.getSubCollectionSizePerVenues(subCollectionName, venues, year)
        view = self.jinja_env.get_template('views/column_chart.html')
        return view.render(
            title="Number of {} for venues {} in {}".format(
                subCollectionName, venues, year),
            xLabel="Venue",
            yLabel="Number of {}".format(subCollectionName),
            data=data
        )

    def trend3(self, n, elementType, filterKeys, filterValues):
        data = self.model.getTopNElements(n, elementType, filterKeys, filterValues)
        view = self.jinja_env.get_template('views/column_chart.html')
        return view.render(
            title="Top {} {} for {} '{}'".format(
                n, elementType, " / ".join(filterKeys), " / ".join(filterValues)),
            xLabel=elementType,
            yLabel="Number of Occurences",
            data=data
        )

    def trend4(self, author, group):
       nodes,edges =  self.model.getRelationAuthor(author, group)
       view = self.jinja_env.get_template('views/graph.html')
       return view.render(nodes=nodes, edges=edges)
    # -------------------------------------------------------------------------
    #   A4 Questions
    # -------------------------------------------------------------------------

    def question1(self):
        self.model.loadJsonFile()
        data = self.model.getTopAuthByVenue(10, "arXiv")
        view = self.jinja_env.get_template('views/question1.html')
        return view.render(data=data)

    def question2(self):
        data = self.model.getPaperMostCited(5, "arXiv")
        view = self.jinja_env.get_template('views/question2.html')
        return view.render(data=data)

    def question3(self):
        self.model.loadJsonFile()
        data = self.model.getAmountPublicationPerYear("ICSE")
        view = self.jinja_env.get_template('views/question3.html')
        return view.render(data=data)

    def question4(self):
        self.model.loadJsonFile()
        nodes, edges = self.model.getCitationTreeByPaper(
            "Low-density parity check codes over GF(q)", 2)
        view = self.jinja_env.get_template('views/question4.html')
        return view.render(nodes=nodes, edges=edges)

    def question5(self):
        self.model.loadJsonFile()
        data = self.model.getNumberOfTimeCitedPerYear(2000, 2016, "Yoshua Bengio")
        view = self.jinja_env.get_template('views/question5.html')
        return view.render(data=data)
