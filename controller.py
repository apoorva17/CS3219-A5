from jinja2 import Environment, FileSystemLoader, select_autoescape


class Controller(object):
    def __init__(self, model):
        self.jinja_env = Environment(
            loader=FileSystemLoader('./'),
            autoescape=select_autoescape(['html'])
        )
        self.model = model

    def index(self):
        view = self.jinja_env.get_template('views/index.html')
        return view.render()

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
