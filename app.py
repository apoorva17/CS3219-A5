"""CS3219 A5 CIR Application.

This file handles all the routing and sets up the Model & Controller.
"""

from flask import Flask, request
from controller import Controller
from model import Model

app = Flask(__name__)
model = Model()
controller = Controller(model)


@app.route('/')
def index():
    return controller.index()


# -------------------------------------------------------------------------
#   A5 Questions
# -------------------------------------------------------------------------

@app.route('/a5/trend1')
def trend1():
    subCollectionName = request.args.get('subCollectionName', default="authors", type=str)
    venue = request.args.get('venue', default="arXiv", type=str)
    yearMin = request.args.get('yearMin', default=2000, type=int)
    yearMax = request.args.get('yearMax', default=2017, type=int)
    return controller.trend1(subCollectionName, venue, yearMin, yearMax)


@app.route('/a5/trend2')
def trend2():
    subCollectionName = request.args.get('subCollectionName', default="authors", type=str)
    venues = request.args.get('venues', default="arXiv,Journal of abnormal child psychology", type=str).split(",")
    year = request.args.get('year', default=2000, type=int)
    return controller.trend2(subCollectionName, venues, year)


@app.route('/a5/trend3')
def trend3():
    n = request.args.get('n', default=10, type=int)
    elementType = request.args.get('elementType', default="authors", type=str)
    filterKeys = request.args.get('filterKeys', default="venue", type=str).split(",")
    filterValues = request.args.get('filterValues', default="ICSE", type=str).split(",")
    return controller.trend3(n, elementType, filterKeys, filterValues)


@app.route('/a5/trend4')
def trend4():
    author = request.args.get('author', default="arXiv", type=str)
    group = request.args.get('group', default="arXiv", type=str)
    return controller.trend4(author, group)


# -------------------------------------------------------------------------
#   A4 Questions
# -------------------------------------------------------------------------

@app.route('/a4/q1')
def question1():
    return controller.question1()


@app.route('/a4/q2')
def question2():
    return controller.question2()


@app.route('/a4/q3')
def question3():
    return controller.question3()


@app.route('/a4/q4')
def question4():
    return controller.question4()


@app.route('/a4/q5')
def question5():
    return controller.question5()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
