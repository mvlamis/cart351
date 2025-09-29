from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return '<h1> Hello CART 351!</h1>'

@app.route("/about")
def about():
    return '<h1 style = "color:purple"> About Cart 351!</h1>'

@app.route("/user/<name>")
def user_profile(name):
    # we will use templates sooN!
    return f"<h2> This is <span style = 'color:orange'>{name}'s</span> profile page"

@app.route("/another/<dynamicVar>")
def another_route(dynamicVar):
    # we will use templates sooN!
    return f"<h2> the 100th letter of {dynamicVar} is {dynamicVar[99]}</h2>"

@app.route("/catlatin/<catname>")
def catlatin(catname):
    if not catname.endswith("y"):
        catname = catname + "y"
    else:
        catname = catname[:-1] +'iful'

    return f"<h2>{catname}</h2>"

app.run(port=5001, debug=True)