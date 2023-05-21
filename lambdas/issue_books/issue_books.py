import json
import boto3
import pymysql
from datetime import timedelta, date
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def get_book_details(connection, book_id):
    cursor = connection.cursor()
    cursor.callproc('search_book_by_book_id', [book_id])

    book = {}
    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            book = {'id': row[0],
                    'title': row[1],
                    'genre': row[2],
                    'author': row[3],
                    'qty': row[4],
                    'status': row[5]
                    }
    return book


def get_date(weeks):
    new_date = date.today()
    if weeks != 0:
        new_date = new_date + timedelta(weeks=weeks)

    return new_date.strftime('%Y-%m-%d')


def handler(event, context):
    connection = None
    try:
        print(event)
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        user_id = event['user_id']
        book_id = event['book_id']

        result = {'book_id': book_id}
        book_details = get_book_details(connection, book_id)
        if not book_details:
            result['issue_status'] = 'fail'
            result['reason'] = 'BookId is not valid! No such book is available!'

        elif 'qty' in book_details and book_details.get('qty') != 0:
            result['title'] = book_details['title']
            result['author'] = book_details['author']

            cursor = connection.cursor()
            issue_date = get_date(0)
            expected_return_date = get_date(1)
            cursor.callproc('issue_book', [user_id, book_id, issue_date, expected_return_date, 0, 'issued'])
            cursor.callproc('update_book_record_on_issue', [book_id, book_details.get('qty') - 1])
            result['issue_status'] = 'success'
            result['issue_date'] = issue_date
            result['expected_return_date'] = expected_return_date

        else:
            result['issue_status'] = 'fail'
            result['reason'] = 'Book is not available right now!'

        return result

    except Exception as e:
        print("Exception occurred:{}".format(e))
        result = {
            'status': 'fail',
            'message': format(e)
        }

    finally:
        connection.close()

    return result
