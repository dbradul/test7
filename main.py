import datetime
import random
import re
import string

import requests

from flask import jsonify, Response, render_template

from flask import Flask
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import use_kwargs

from db import execute_query
from http_status import HTTP_200_OK, HTTP_204_NO_CONTENT
from utils import format_records, profile

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


@app.route('/customers')
@use_kwargs(
    {
        "first_name": fields.Str(
            required=False,
            missing=None,
            validate=[validate.Regexp('^[0-9]*')]
        ),
        "last_name": fields.Str(
            required=False,
            missing=None,
            validate=[validate.Regexp('^[0-9]*')]
        ),
    },
    location="query",
)
def get_customers(first_name, last_name):
    query = 'select * from customers'

    fields = {}
    if first_name:
        fields["FirstName"] = first_name

    if last_name:
        fields["LastName"] = last_name

    if fields:
        query += ' WHERE ' + ' AND '.join(f'{k}="{v}"' for k, v in fields.items())

    records = execute_query(query)
    result = format_records(records)
    return result



@app.route('/customers2')
@use_kwargs(
    {
        "text": fields.Str(
            required=False,
            missing=None,
        ),
    },
    location="query",
)
@profile()
def get_customers2(text):
    query = 'select * from customers'
    records = execute_query(query)

    text_fields = ['FirstName', 'LastName', 'Email']
    results = []
    if text:
        for rec in records:
            if any(text in str(field) for field in rec if field in text_fields):
                results.append(rec)
    else:
        results = records

    result = format_records(results)
    return result


@app.route('/customers3')
@use_kwargs(
    {
        "text": fields.Str(
            required=False,
            missing=None,
        ),
    },
    location="query",
)
@profile()
def get_customers3(text):
    query = 'select * from customers'

    text_fields = ['CustomerId', 'FirstName', 'LastName', 'Email']

    if text:
        query += ' WHERE ' + ' OR '.join(f'{field} like ?' for field in text_fields)

    records = execute_query(query, (f'%{text}%',) * len(text_fields))
    result = format_records(records)

    return result


app.run(port=5004, debug=True)


