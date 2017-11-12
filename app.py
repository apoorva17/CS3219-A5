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
    subCollectionName = request.args.get('subCollectionName', type=str) or "authors"
    venue = request.args.get('venue', type=str) or "arXiv"
    yearMin = request.args.get('yearMin', type=int) or 2000
    yearMax = request.args.get('yearMax', type=int) or 2016
    return controller.trend1(subCollectionName, venue, yearMin, yearMax)


@app.route('/a5/trend2')
def trend2():
    subCollectionName = request.args.get('subCollectionName', type=str) or "authors"
    venues = request.args.get('venues', type=str) or "arXiv,ICSE"
    venues = venues.split(",")
    year = request.args.get('year', type=int) or 2000
    return controller.trend2(subCollectionName, venues, year)


@app.route('/a5/trend3')
def trend3():
    n = request.args.get('n', type=int) or 10
    elementType = request.args.get('elementType', type=str) or "authors"
    filterKeys = request.args.get('filterKeys', type=str) or "venue"
    filterKeys = filterKeys.split(",")
    filterValues = request.args.get('filterValues', type=str) or "ICSE"
    filterValues = filterValues.split(",")
    return controller.trend3(n, elementType, filterKeys, filterValues)


@app.route('/a5/trend4')
def trend4():
    author = request.args.get('author', type=str) or "Lin Li"
    group = request.args.get('group', type=str) or "year"
    return controller.trend4(author, group)


@app.route('/a5/trend5')
def trend5():
    title = request.args.get('title', type=str) or "Low-density parity check codes over GF\(q\)"
    maxDepth = request.args.get('maxDepth', type=int) or 1
    return controller.trend5(title, maxDepth)


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
