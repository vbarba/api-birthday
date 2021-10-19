import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

from flask_lambda import FlaskLambda
from flask import request,jsonify

EXEC_ENV = os.environ['EXEC_ENV']
REGION = os.environ['REGION_NAME']
TABLE_NAME = os.environ['TABLE_NAME']

app = FlaskLambda(__name__)

if EXEC_ENV == 'local':
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://127.0.0.1:8000')
else:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)

def db_table(table_name=TABLE_NAME):
    return dynamodb.Table(table_name)

def calculate_days(birthday):
    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    delta1 = (datetime(now.year, birthday.month, birthday.day) - now).days
    # There is a corner case of users born in a leap year (29 february) that should be handled
    delta2 = (datetime(now.year+1, birthday.month, birthday.day) - now).days
    
    return delta1 if delta1 >= 0 else delta2

@app.route('/hello/<string:username>', methods=('PUT',))
def put_hello(username):
    if not username.isalpha():
        return jsonify({"message": "Names are made of letters!"}), 403
    birthday = request.json['dateOfBirth']
    now = datetime.now()
    if datetime.strptime(birthday, '%Y-%m-%d') < now:
        tbl_response = db_table().put_item(
        Item={
                'username': username,
                'birthday': birthday
            }
        )
        return jsonify()
    else:
        return jsonify({"message": "Youren't born yet!"}),403

@app.route('/hello/<string:username>', methods=('GET',))
def get_hello(username):

    tbl_response = db_table().get_item(Key={'username': username}) 

    birthday = datetime.strptime(tbl_response['Item']['birthday'], '%Y-%m-%d')
    days_to_birthday = calculate_days(birthday)

    if days_to_birthday > 0:
        message = "Hello, "+username+"! Your birthday is in "+str(days_to_birthday)+" day(s)"
    else:
        message = "Hello, "+username+"! Happy birthday!"

    return jsonify({"message": message})
