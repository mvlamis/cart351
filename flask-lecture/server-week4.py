from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("pineapples.html")

@app.route('/another')
def another():
    return render_template("pineapples_2.html")

@app.route('/three')
def three():
    someNewVar = "Michael"
    someList = ["one","two","three"]
    someDict = {"color":"yellow", "feature":"spiky","taste":"delicious"}
    return render_template("pineapples_3.html",
                           my_variable = someNewVar, 
                           my_list = someList,
                           my_dict = someDict)

@app.route('/four')
def four():
    a_new_list = [1,2,3,4,5]
    b_new_list = ["yellow","orange","blue", "green", "turquoise","fuscia","navy"]
    userLoggedIn = False
    
    return render_template("pineapples_4.html",
                            a_num_list = a_new_list, 
                            color_list =  b_new_list, 
                            userLoggedIn = userLoggedIn  )

@app.route('/lemons')
def lemons():
    animals = ['lions', 'tigers', 'bears', 'monkeys', 'green women']
    lemon_bool = True
    return render_template("lemons.html",
                           animals = animals,
                           lemon_bool = lemon_bool,
                           )


app.run(port=5001, debug=True)