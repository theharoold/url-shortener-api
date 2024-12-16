from flask import Flask, redirect, jsonify, request 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func, text 
from http import HTTPStatus
import yaml 
from functools import wraps 

with open('config/config.yaml') as f:
    config = yaml.load(f, yaml.Loader)

app = Flask(__name__)
# Setup DSN
app.config['SQLALCHEMY_DATABASE_URI'] = f"{config['db']['dbms']}://{config['db']['username']}:{config['db']['password']}" +\
f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class URLS(db.Model):
    short_url = db.Column(db.String(50), primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class TOKENS(db.Model):
    token = db.Column(db.String(255), primary_key=True)

# Create URLS and TOKENS tables if they don't already exist
with app.app_context():
    db.create_all()

def authenticate(f):
    @wraps(f)
    def decoratorFunction(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if auth_token is None:
            return jsonify({'message': "Missing authorization token"}), HTTPStatus.UNAUTHORIZED

        # First we need to check whether the user is authorized to create a short url
        tokens = db.session.execute(text("SELECT token FROM TOKENS")).scalars().all()

        if auth_token not in tokens:
            return jsonify({'message': "Invalid token"}), HTTPStatus.UNAUTHORIZED
        
        return f(*args, **kwargs)
    return decoratorFunction

@app.route("/<short_url>", methods=["GET"])
def decodeShortURL(short_url):
    url = db.session.execute(db.select(URLS).filter_by(short_url=short_url)).scalar_one_or_none()
    if not url:
        return jsonify({"message": "URL Not Found"}), HTTPStatus.NOT_FOUND

    return redirect(url.url, HTTPStatus.TEMPORARY_REDIRECT)

@app.route("/", methods=["POST", "PUT"])
@authenticate
def encodeShortURL():
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"message": "Invalid POST body"}), HTTPStatus.BAD_REQUEST

    now = func.now()

    required = ['url', 'short_url']
    for field in required:
        if field not in data:
            return jsonify({"message": "Missing one of the required fields - url or short_url"}), HTTPStatus.BAD_REQUEST

    url = data.get('url')
    short_url = data.get('short_url')

    # Check if short_url already exists
    # But only for creating a new short_url
    # Updating should create new or replace existing short_url (PUT)
    if request.method == "POST":
        match = db.session.execute(db.select(URLS).filter_by(short_url=short_url)).scalar_one_or_none()
        if match is not None:
            return jsonify({"message": "Short URL already exists"}), HTTPStatus.CONFLICT

    if request.method == "POST":
        shortened = URLS(url=url, short_url=short_url, created_at=now)
        db.session.add(shortened)
    else:
        shortened = URLS.query.filter_by(short_url=short_url).first()
        shortened.url = url 
        shortened.created_at = now
    try:
        db.session.commit()
    except Exception as e: 
        return jsonify({"message": "Insert unsuccessful"}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    return jsonify({
        "url": shortened.url,
        "short_url": shortened.short_url,
        "created_at": shortened.created_at
    }), HTTPStatus.CREATED

if __name__ == '__main__':
    app.run()