from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def default():
    return render_template("base.html")

@app.route('/index')
def index():
    user = {"username":"sabine"}
    passedDictionary = {
        "fav_color":"fuscia", 
        "fav_veg":"cauliflower",
        "fav_fruit":"kiwi",
        "fav_animal":"toucan"
    }
    imgPath = "pineapple_2.jpg"

    return render_template("index.html",
                           user=user,
                           passedDictionary=passedDictionary,
                           imgPath=imgPath
                           )

@app.route('/pineParent')
def pineapple_parent():
    return render_template("pineappleParent.html")

@app.route("/about")
def pineappleChild():
    return render_template("pineappleChild.html",
                           dataPassedA = "child A!" )

@app.route("/addPlantData")
def addPlantData():
    return render_template("addPlantData.html")

@app.route("/thank_you")
def thank_you():
    app.logger.info(request.args)
    return render_template("thankyou.html",owner_name = request.args["o_name"])

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/reg_thank_you",methods = ['POST', 'GET'])
def reg_thank_you():
    fName = request.form["f_name"]
    lName = request.form["l_name"]
    return render_template("thankyou_reg.html", fName = fName, lName=lName)

@app.route("/inputPlantEx")
def addPlantDataEx():
    return render_template("addPlantDataExtended.html")

@app.route("/thank_plant_two",methods = ['POST', 'GET'])
def thank_you_two():
    return render_template("thankyou_plant_rev.html")

app.run(debug=True)