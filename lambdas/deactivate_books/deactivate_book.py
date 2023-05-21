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

        status = event['status']
        book_id = event['book_id']

        if status == 'success':
            cursor = connection.cursor()
            cursor.callproc('deactivate_book', [book_id])
            event['status'] = 'Book is deactivated successfully!'

    except Exception as e:
        print("Exception occurred:{}".format(e))
        event['status'] = 'fail'
        event['message'] = format(e)

    finally:
        connection.close()

    return event
