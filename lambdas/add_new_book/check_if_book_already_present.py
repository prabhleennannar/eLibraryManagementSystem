import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def check_if_book_already_exists(connection, body):
    title = body['title']
    author = body['author']

    cursor = connection.cursor()
    cursor.callproc('list_all_books')

    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            if title == str(row[1]) and author == str(row[3]):
                return True

    return False


def handler(event, context):
    connection = None
    try:
        request = event['request']

        sm_response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(sm_response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        response = {'is_present': True, 'requested_details': request}
        if check_if_book_already_exists(connection, request):
            response['message'] = 'The book with title ' + request['title'] + ' and author ' + request[
                'author'] + ' already exists!'

        else:
            response['is_present'] = False

    except Exception as e:
        print("Exception occurred:{}".format(e))
        response = {
            'is_present': True,
            'message': format(e)
        }

    finally:
        connection.close()

    return response
