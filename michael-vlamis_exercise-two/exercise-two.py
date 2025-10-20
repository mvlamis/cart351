from flask import Flask,render_template,request
import os
app = Flask(__name__)


# the default route
@app.route("/")
def index():
      return render_template("index.html")

#*************************************************

#Task: Variables and JinJa Templates
@app.route("/t1")
def t1():
      the_topic = "donuts"
      number_of_donuts = 28
      donut_data= {
      "flavours":["Regular", "Chocolate", "Blueberry", "Devil's Food"],
      "toppings": ["None","Glazed","Sugar","Powdered Sugar",
                   "Chocolate with Sprinkles","Chocolate","Maple"]
                   }
      
      icecream_flavors = ["Vanilla","Raspberry","Cherry", "Lemon"]
      return render_template("t1.html",
                             topic=the_topic,
                             num_donuts=number_of_donuts,
                             donut_data=donut_data,
                             icecream_flavors=icecream_flavors)

#*************************************************

#Task: HTML Form get & Data 
@app.route("/t2")
def t2():
    return render_template("t2.html")

@app.route("/thank_you_t2", methods=['GET'])
def thank_you_t2():
    # get form data from GET request
    name = request.args.get('name', '')
    email = request.args.get('email', '')
    order_description = request.args.get('order-description', '')
    
    # combine all three data points into one string
    combined_string = f"{name} {email} {order_description}"
    
    # replace vowels with asterisks
    vowels = "aeiouAEIOU"
    modified_string = ""
    for char in combined_string:
        if char in vowels:
            modified_string += "*"
        else:
            modified_string += char
    
    return render_template("thankyou_t2.html", modified_text=modified_string)

#*************************************************

#run
app.run(debug=True)