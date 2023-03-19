from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hellocddsd Wssld! this is the newest version"