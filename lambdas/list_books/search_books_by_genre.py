import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def get_book_based_on_genre(connection, genre):
    cursor = connection.cursor()
    cursor.callproc('get_book_based_on_genre', [genre])

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
    connection = None
    response = {'requested_details': event}
    try:
        sm_response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(sm_response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        genre = event['name']
        books = get_book_based_on_genre(connection, genre)

        if not books:
            response['status'] = 'fail'
            response['message'] = 'The books with genre ' + str(genre).upper() + ' are not available!'

        else:
            response['status'] = 'success'
            response['message'] = 'The books with genre ' + str(genre).upper() + ' are as below!'
            response['books_list'] = books

    except Exception as e:
        print("Exception occurred:{}".format(e))
        response = {
            'status': 'fail',
            'message': format(e)
        }

    finally:
        connection.close()

    return response
