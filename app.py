from flask import Flask, redirect, jsonify 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func 
from http import HTTPStatus
import yaml 

with open('config/config.yaml') as f:
    config = yaml.load(f, yaml.Loader)

app = Flask(__name__)
# Setup DSN
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{config['db']['username']}:{config['db']['password']}" +\
f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class URLS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    short_url = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class TOKENS(db.Model):
    token = db.Column(db.String(255), primary_key=True)

# Create URLS and TOKENS tables if they don't already exist
with app.app_context():
    db.create_all()

@app.route("/<short_url>", methods=["GET"])
def decodeShortURL(short_url):
    url = db.session.execute(db.select(URLS).filter_by(short_url=short_url)).scalar_one_or_none()
    if not url:
        return jsonify({"message": "URL Not Found"}), HTTPStatus.NOT_FOUND

    return redirect(url.url, HTTPStatus.PERMANENT_REDIRECT)

@app.route("/", methods=["POST"])
def encodeShortURL():
    # Placeholder
    return HTTPStatus.CREATED 

if __name__ == '__main__':
    app.run()