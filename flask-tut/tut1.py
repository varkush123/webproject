from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello ():
   return "Hello World"

@app.route("/harry")
def varsha ():
   return "Hello Worl"

app.run(debug = True)