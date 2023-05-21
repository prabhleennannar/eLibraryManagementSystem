import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def handler(event, context):
    connection = None
    try:
        del event['is_present']
        requested_details = event['requested_details']

        sm_response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(sm_response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        cursor = connection.cursor()
        cursor.callproc('add_new_book',
                        [requested_details['title'], requested_details['genre'], requested_details['author'],
                         requested_details['qty'], 'active'])

        event['status'] = 'success'
        event['message'] = 'The book with title ' + requested_details['title'] + ' and author ' + requested_details[
            'author'] + 'is successfully added!'

    except Exception as e:
        print("Exception occurred:{}".format(e))
        event['status'] = 'fail'
        event['message'] = format(e)

    finally:
        connection.close()

    return event
