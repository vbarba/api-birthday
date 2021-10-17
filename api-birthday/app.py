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
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://dynamodb:8000')
else:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)


def db_table(table_name=TABLE_NAME):
    return dynamodb.Table(table_name)

def parse_user_id(req):
    '''When frontend is built and integrated with an AWS Cognito
       this will parse and decode token to get user identification'''
    return req.headers['Authorization'].split()[1]

def calculate_days(birthday):
    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    delta1 = (datetime(now.year, birthday.month, birthday.day) - now).days
    delta2 = (datetime(now.year+1, birthday.month, birthday.day) - now).days
    
    return delta1 if delta1 >= 0 else delta2

@app.route('/hello/<string:username>', methods=('PUT',))
def put_hello(username):
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

# @app.route('/lists/<string:list_id>')
# def fetch_list(list_id):
#     try:
#         user_id = parse_user_id(request)
#     except:
#         return jsonify('Unauthorized'), 401

#     tbl_response = db_table().get_item(Key={'userId': user_id, 'listId': list_id})
#     return jsonify(tbl_response['Item'])


# @app.route('/lists/<string:list_id>', methods=('PUT',))
# def update_list(list_id):
#     try:
#         user_id = parse_user_id(request)
#     except:
#         return jsonify('Unauthorized'), 401

#     list_data = {k: {'Value': v, 'Action': 'PUT'}
#                 for k, v in request.get_json().items()}
#     tbl_response = db_table().update_item(Key={'userId': user_id, 'listId': list_id},
#                                           AttributeUpdates=list_data)
#     return jsonify()


# @app.route('/lists/<string:list_id>', methods=('DELETE',))
# def delete_list(list_id):
#     try:
#         user_id = parse_user_id(request)
#     except:
#         return jsonify('Unauthorized'), 401

#     db_table().delete_item(Key={'userId': user_id, 'listId': list_id})
#     return jsonify()


# @app.route('/lists')
# def fetch_lists():
#     try:
#         user_id = parse_user_id(request)
#     except:
#         return jsonify('Unauthorized'), 401

#     tbl_response = db_table().query(KeyConditionExpression=Key('userId').eq(user_id))
#     return jsonify(tbl_response['Items'])

