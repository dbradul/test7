import datetime
import random
import string

import requests

from flask import jsonify, Response, render_template

from flask import Flask
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import use_kwargs

from http_status import HTTP_200_OK, HTTP_204_NO_CONTENT

app = Flask(__name__)


@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/now")
def get_current_time():
    return str(datetime.datetime.now())

@app.route("/password")
@use_kwargs(
    {
        "length": fields.Int(
            # required=True,
            missing=10,
            validate=[validate.Range(min=1, max=999)],
        ),
        "specials": fields.Bool(
            missing=False,
            validate=[validate.Range(min=0, max=1)],
        ),
    },
    location="query",
)
def generate_password(length, specials):
    render_template('error.html', error_code='The request was unsuccessful.')
    return ''.join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase,
            k=length,
        )
    )

@app.route('/who-is-on-duty')
def get_astronauts():
    url = 'http://api.open-notify.org/astros.json'
    res = requests.get(url)
    if res.status_code not in (HTTP_200_OK, HTTP_204_NO_CONTENT):
        return Response(f'ERROR: Something went wrong: {res.status_code}', status=res.status_code)
    result = res.json()
    stats = {}
    for entry in result['people']:
        stats[entry['craft']] = stats.get(entry['craft'], 0) + 1
    return stats

app.run(port=5004, debug=True)
