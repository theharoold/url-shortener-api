# url-shortener-api v0.1
Python Flask API for a URL Shortener

Stack: Flask + SQLAlchemy

The purpose of this REST API is to redirect users to a specific website using a "shortened URL". For example, if one were to target
GET /<short_url> route, if such a mapping (short_url -> url) exists in the database, the user would be redirected to url from the database.

## Functionalities

- Users can use short url to get a redirect to a desired destination url. 
- Users can **create** or **replace** a short_url record if they are properly authenticated.

## Routes

- `GET /<short_url>` - returns a redirect to destination URL 

Example request:

*Request:*

`GET /hello_world`

*Response:*

`302 TEMPORARY REDIRECT https://www.google.com`

In this case, "hello_world" is the short url, and "https://www.google.com" is the destination url. 


- `POST /` - create new short url record

Will return 409 CONFLICT if a short_url already exists. If you want to replace the URL current short_url points to,
use PUT / instead (below).

Be sure to include your authorization token in 'Authorization' header field. It is compared to existing tokens from table TOKENS.

By default, short_url will the any value you pass to it, as long as it is <=50 characters long. Perhaps I'll add hashing in the future,
but for now it is enough for me to have complete control over short_url values. 

Example request:

`POST / HTTP/1.1`
`Authorization: token`
`Content-Type: application/json`

`{`
`    "short_url": "my-website",`
`    "url": "https://www.mywebsite.com"`
`}`

Example response:

`201 CREATED`

`{`
`   "created_at": "timestamp",`
`    "short_url": "my-website",`
`    "url": "https://www.mywebsite.com"`
`}`

- `PUT /` - replace (or create if it doesn't exist) short url record

Usage is the same as with `POST /`, example is given above, with a slight exception - this one is used to create **or replace** a short_url.

## Error messages

If the request fails at any point, you will receive a response that looks like this:

`ERROR_CODE`

`{`
`   "message": "error message with more details"`   
`}`

## Database Tables

1. URLS
2. TOKENS

Both tables are created using SQLAlchemy and have the following fields:

**Table URLS:**
- short_url String(50) PRIMARY KEY 
- url String(255) NOT NULL
- created_at TIMESTAMP DEFAULT NOW() NOT NULL

Table URLS holds short_url -> url mapping for redirecting purposes.

**Table TOKENS:**
- token String(50) PRIMARY KEY

Token is used for authentication purposes.
You can use `INSERT INTO TOKENS VALUES ('my_token')` to insert a token into the database.

