from flask import Flask,render_template,request
import os
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads' # Or os.path.join(app.instance_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit

# the default route
@app.route("/")
def index():
      return render_template("index.html")

#*************************************************
#Task: CAPTURE & POST & FETCH & SAVE
@app.route("/t2")
def t2():
    return render_template("t2.html")

@app.route("/postDataFetch",methods = ['POST', 'GET'])
def postDataFetch():
    data = request.get_json()
    # append data to data.txt
    with open('files/data.txt', 'a') as f:
        f.write(f"{data['x']},{data['y']},{data['imageIndex']},{data['size']}\n")
    return "Data received", 200

@app.route("/allFireworks.html")
def allFireworks():
    # jsonify data from data.txt
    with open('files/data.txt', 'r') as f:
        lines = f.readlines()
    fireworks_data = []
    for line in lines:
        x, y, imageIndex, size = line.strip().split(',')
        fireworks_data.append({'x': x, 'y': y, 'imageIndex': int(imageIndex), 'size': size})
    return render_template("allFireworks.html", fireworks_data=fireworks_data)

#*************************************************
#run
app.run(debug=True, port=5001)