import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def handler(event, context):
    connection = None
    try:
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        book_id = event
        print(book_id)
        cursor = connection.cursor()
        cursor.callproc('get_issued_book_based_on_book_id', [book_id])
        result = {
            'book_id': book_id
        }
        if cursor.rowcount != 0:
            result['status'] = 'fail'
            result['message'] = 'Book is borrowed by users! Deactivation cannot be performed!'
        else:
            result['status'] = 'success'

    except Exception as e:
        print("Exception occurred:{}".format(e))
        result = {
            'status': 'fail',
            'message': format(e)
        }

    finally:
        connection.close()

    return result
