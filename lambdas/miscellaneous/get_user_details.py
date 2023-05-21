import boto3
import json
import pymysql
import os

sm_client = boto3.client('secretsmanager')
cognito_client = boto3.client('cognito-idp')
mysql_secret = os.environ['mysql_secret']


def get_user_issued_books(connection, user_id):
    cursor = connection.cursor()
    cursor.callproc('get_user_issued_books', [user_id])

    issued_book_details = []
    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            user_detail = {'book_id': row[0],
                           'title': row[1],
                           'genre': row[2],
                           'author': row[3],
                           'borrow_date': json.dumps(row[4], default=str),
                           'default_return_date': json.dumps(row[5], default=str),
                           'status': row[6]
                           }
            issued_book_details.append(user_detail)

    return issued_book_details


def get_user_returned_books(connection, user_id):
    cursor = connection.cursor()
    cursor.callproc('get_user_returned_books', [user_id])

    returned_book_details = []
    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            user_detail = {'book_id': row[0],
                           'title': row[1],
                           'genre': row[2],
                           'author': row[3],
                           'borrow_date': json.dumps(row[4], default=str),
                           'default_return_date': json.dumps(row[5], default=str),
                           'actual_return_date': json.dumps(row[6], default=str),
                           'fine': row[7],
                           'status': row[8]
                           }
            returned_book_details.append(user_detail)

    return returned_book_details


def handler(event, context):
    authorizer = event['requestContext']['authorizer']
    user_id = authorizer['sub']

    connection = None
    try:
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        user_issued_book_details = get_user_issued_books(connection, user_id)
        user_returned_book_details = get_user_returned_books(connection, user_id)
        result = {
            'status': 'success',
            'issued_book_details': user_issued_book_details,
            'returned_book_details': user_returned_book_details
        }

    except Exception as e:
        print("Exception occurred:{}".format(e))
        result = {
            'status': 'fail',
            'message': format(e)
        }

    finally:
        connection.close()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(result)
    }
