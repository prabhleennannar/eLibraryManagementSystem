import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def get_books(connection):
    cursor = connection.cursor()
    cursor.callproc('list_all_books')

    books = []
    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            book = {'id': row[0],
                    'title': row[1],
                    'genre': row[2],
                    'author': row[3],
                    'qty': row[4],
                    'status': row[5]
                    }
            books.append(book)

    return books


def handler(event, context):
    try:
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        response = {'requested_details': event}
        books = get_books(connection)
        print(books)

        if not books:
            response['status'] = 'fail'
            response['message'] = 'There are no books available at the moment!'

        else:
            response['status'] = 'success'
            response['message'] = 'All the books are listed below!'
            response['books_list'] = books

        return response

    except Exception as e:
        print("Exception occurred:{}".format(e))
        response = {
            'status': 'fail',
            'message': format(e)
        }
        return response
