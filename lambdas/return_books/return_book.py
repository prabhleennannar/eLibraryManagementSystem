import json
import boto3
import pymysql
from datetime import date
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def handler(event, context):
    connection = None
    result = {}
    try:
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        user_id = event['user_id']
        book_id = event['book_id']
        status = event['status']
        result = {
            'book_id': book_id
        }

        if status == 'success':
            cursor = connection.cursor()
            fine = event['calculated_fine']
            cursor.callproc('return_book', [user_id, book_id, date.today().strftime('%Y-%m-%d'), fine])

            cursor.callproc('get_book_based_on_id', [book_id])
            qty = 0
            title = None
            author = None
            if cursor.rowcount != 0:
                for row in cursor.fetchall():
                    qty = row[4]
                    title = row[1]
                    author = row[2]

            cursor.callproc('update_book_record', [book_id, qty + 1])
            result['status'] = 'success'
            result['message'] = 'Book is successfully returned!'
            result['title'] = title
            result['author'] = author
            result['fine'] = fine

        else:
            result['status'] = 'fail'
            result['message'] = 'No such book is issued!'

    except Exception as e:
        print("Exception occurred:{}".format(e))
        result['status'] = 'fail'
        result['message'] = format(e)

    finally:
        connection.close()

    return result
