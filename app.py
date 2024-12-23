from flask import Flask, redirect, jsonify, request, render_template 
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS 
from flask_limiter import Limiter 
from flask_limiter.util import get_remote_address 
from sqlalchemy import func, text 
from http import HTTPStatus
import yaml 
from functools import wraps 

with open('config/config.yaml') as f:
    config = yaml.load(f, yaml.Loader)

app = Flask(__name__)
cors = CORS(app)
# Setup DSN
app.config['SQLALCHEMY_DATABASE_URI'] = f"{config['db']['dbms']}://{config['db']['username']}:{config['db']['password']}" +\
f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per second"]
)

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
        tokens = db.session.execute(text("SELECT token FROM tokens")).scalars().all()

        if auth_token not in tokens:
            return jsonify({'message': "Invalid token"}), HTTPStatus.UNAUTHORIZED
        
        return f(*args, **kwargs)
    return decoratorFunction

@app.route("/", methods=["GET"])
@limiter.limit("5 per second")
def returnHomeTemplate():
    return render_template('index.html')

@app.route("/<short_url>", methods=["GET"])
@limiter.limit("5 per second")
def decodeShortURL(short_url):
    url = db.session.execute(db.select(URLS).filter_by(short_url=short_url)).scalar_one_or_none()
    if not url:
        return jsonify({"message": "URL Not Found"}), HTTPStatus.NOT_FOUND

    return redirect(url.url, HTTPStatus.TEMPORARY_REDIRECT)

@app.route("/", methods=["POST", "PUT"])
@limiter.limit("5 per second")
@authenticate
def encodeShortURL():
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"message": "Invalid POST body"}), HTTPStatus.BAD_REQUEST

    now = func.now()

    required = ['short_url', 'url']
    for field in required:
        if field not in data:
            return jsonify({"message": "Missing one of the required fields - url or short_url"}), HTTPStatus.BAD_REQUEST

    url = data.get('url')
    short_url = data.get('short_url')
    if len(url) > 255 or len(short_url) > 50:
        return jsonify({"message": "URL or short URL are too long"}), HTTPStatus.BAD_REQUEST

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
        if not shortened:
            shortened = URLS(url=url, short_url=short_url, created_at=now)
            db.session.add(shortened)
        else:
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

@app.route("/", methods=["DELETE"])
@limiter.limit("5 per second")
@authenticate
def deleteShortURL():
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"message": "Invalid POST body"}), HTTPStatus.BAD_REQUEST
    
    key = data.get('short_url')
    if key is None:
        return jsonify({"message": "Missing required field - short_url"}), HTTPStatus.BAD_REQUEST
    
    url = db.session.query(URLS).get(key)
    if url is None:
        return jsonify({"message": "URL Not Found"}), HTTPStatus.NOT_FOUND
    else:
        try:
            db.session.delete(url)
            db.session.commit()
        except Exception as e:
            return jsonify({"message": "Delete unsuccessful"}), HTTPStatus.INTERNAL_SERVER_ERROR
        
        print(jsonify({
            "short_url": key
        }))

        return jsonify({
            "short_url": key
        }), HTTPStatus.OK

if __name__ == '__main__':
    app.run()
