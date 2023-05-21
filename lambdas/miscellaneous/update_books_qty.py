import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def get_book_based_on_book_id(connection, book_id):
    cursor = connection.cursor()
    cursor.callproc('get_book_based_on_id', [book_id])

    book = {}
    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            book['id'] = row[0]
            book['title'] = row[1]
            book['genre'] = row[2]
            book['author'] = row[3]
            book['qty'] = row[4]

    return book


def handler(event, context):
    try:
        body = str(event['body']).replace('\n', '')
        json_body = json.loads(body)

        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        response = {'requested_details': json_body}
        if 'bookId' in json_body and ('add_qty' in json_body or 'minus_qty' in json_body):
            book_id = json_body['bookId']
            book = get_book_based_on_book_id(connection, book_id)
            response['book_details'] = book

            if not book:
                response['status'] = 'fail'
                response['message'] = 'The book with id ' + str(book_id) + ' does not exists!'

            else:
                cursor = connection.cursor()

                new_qty = 0
                status = 'active'
                if 'add_qty' in json_body:
                    new_qty = json_body['add_qty'] + book['qty']

                if 'minus_qty' in json_body:
                    new_qty = book['qty'] - json_body['minus_qty']
                    if new_qty == 0:
                        status = 'inactive'

                if new_qty < 0:
                    response['status'] = 'fail'
                    response['message'] = 'Please check the quantity of book with book_id ' \
                                          '' + str(book_id) + ' in the system first before updating!'

                else:
                    cursor.callproc('update_book_qty', [book_id, new_qty, status])
                    response['status'] = 'success'
                    response['message'] = 'The quantity of book with id ' + str(book_id) + ' is successfully updated!'
                    book_details = response['book_details']
                    book_details['qty'] = new_qty
                    response['book_details'] = book_details

        else:
            response['status'] = 'fail'
            response['message'] = 'Please include "bookId" and "add_qty" or "minus_qty" values in the request!'

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }

    except Exception as e:
        print("Exception occurred:{}".format(e))
        response = {
            'status': 'fail',
            'message': format(e)
        }
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }
