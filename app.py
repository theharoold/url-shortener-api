from flask import Flask, redirect 
from http import HTTPStatus

app = Flask(__name__)

@app.route("/<short_url>", methods=["GET"])
def decodeShortURL(short_url):
    # Placeholder
    return redirect("https://www.google.com", HTTPStatus.PERMANENT_REDIRECT)

@app.route("/", methods=["POST"])
def encodeShortURL():
    # Placeholder
    return HTTPStatus.CREATED 