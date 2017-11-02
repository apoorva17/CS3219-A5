"""CS3219 A5 CIR Application.

This file handles all the routing and sets up the Model & Controller.
"""

from flask import Flask
from controller import Controller
from model import Model

app = Flask(__name__)
model = Model()
controller = Controller(model)


@app.route('/')
def index():
    return controller.index()


@app.route('/1')
def question1():
    return controller.question1()


@app.route('/2')
def question2():
    return controller.question2()


@app.route('/3')
def question3():
    return controller.question3()


@app.route('/4')
def question4():
    return controller.question4()


@app.route('/5')
def question5():
    return controller.question5()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
