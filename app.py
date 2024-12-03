from flask import Flask, redirect 
from http import HTTPStatus
import yaml 

# Need to add SQLAlchemy

app = Flask(__name__)

with open('config/config.yaml') as f:
    config = yaml.load(f, yaml.Loader)

@app.route("/<short_url>", methods=["GET"])
def decodeShortURL(short_url):
    # Placeholder
    return redirect(f"https://www.google.com/?q={short_url}", HTTPStatus.PERMANENT_REDIRECT)

@app.route("/", methods=["POST"])
def encodeShortURL():
    # Placeholder
    return HTTPStatus.CREATED 