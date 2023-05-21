import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def get_user_issued_book_details(connection, user_id):
    cursor = connection.cursor()
    cursor.callproc('get_issued_books_details_with_user_id', [user_id])

    issued_book_details = []
    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            user_detail = {'id': row[0],
                           'book_id': row[2],
                           'borrow_date': json.dumps(row[3], default=str),
                           'default_return_date': json.dumps(row[4], default=str),
                           'actual_return_date': json.dumps(row[5], default=str),
                           'fine': row[6],
                           'status': row[7]
                           }
            issued_book_details.append(user_detail)

    return issued_book_details


def handler(event, context):
    connection = None
    response = {'requested_details': event}
    try:
        sm_response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(sm_response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        user_id = event['user_id']
        user_issued_book_details = get_user_issued_book_details(connection, user_id)
        response['issued_book_details'] = user_issued_book_details

        if len(user_issued_book_details) < 4:
            response['is_eligible'] = True

        else:
            response['is_eligible'] = False
            response['reason'] = 'over limit'

    except Exception as e:
        print("Exception occurred:{}".format(e))
        response = {
            'status': 'fail',
            'message': format(e)
        }

    finally:
        connection.close()

    return response
