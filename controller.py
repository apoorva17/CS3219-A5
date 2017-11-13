from jinja2 import Environment, FileSystemLoader, select_autoescape


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
        data = list(self.model.getSubCollectionSizePerYear(
            subCollectionName=subCollectionName,
            venue=venue,
            yearMin=yearMin,
            yearMax=yearMax,
        ))
        view = self.jinja_env.get_template(
            'views/line_chart.html' if data else 'views/no_data.html')
        return view.render(
            title="Number of {} per year ({}, {}-{})".format(
                subCollectionName, venue, yearMin, yearMax),
            xLabel="Year",
            yLabel="Number of {}".format(subCollectionName),
            data=data,
            form_function="getFormTrend1",
        )

    def trend2(self, subCollectionName, venues, year):
        data = list(self.model.getSubCollectionSizePerVenues(subCollectionName, venues, year))
        view = self.jinja_env.get_template(
            'views/donutchart.html' if data else 'views/no_data.html')
        return view.render(
            title="Number of {} for venues {} in {}".format(
                subCollectionName, venues, year),
            xLabel="Venue",
            yLabel="Number of {}".format(subCollectionName),
            data=data,
            form_function="getFormTrend2",
        )

    def trend3(self, n, elementType, filterKeys, filterValues):
        data = list(self.model.getTopNElements(n, elementType, filterKeys, filterValues))
        view = self.jinja_env.get_template(
            'views/column_chart.html' if data else 'views/no_data.html')
        return view.render(
            title="Top {} {} for {} '{}'".format(
                n, elementType, " / ".join(filterKeys), " / ".join(filterValues)),
            xLabel=elementType,
            yLabel="Number of Occurences",
            data=data,
            form_function="getFormTrend3",
        )

    def trend4(self, author, group):
        nodes, edges = self.model.getRelationAuthor(author, group)
        view = self.jinja_env.get_template(
            'views/graph.html' if nodes else 'views/no_data.html')
        return view.render(
            page_title="Relation of an author",
            nodes=nodes,
            edges=edges,
            form_function="getFormTrend4",
        )

    def trend5(self, title, maxDepth):
        nodes, edges = self.model.getCitationGraph(title, maxDepth)
        view = self.jinja_env.get_template(
            'views/graph.html' if nodes else 'views/no_data.html')
        return view.render(
            page_title="Citation Graph",
            nodes=nodes,
            edges=edges,
            form_function="getFormTrend5",
        )
