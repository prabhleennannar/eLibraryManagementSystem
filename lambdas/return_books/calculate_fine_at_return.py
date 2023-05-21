import json
import boto3
import pymysql
from datetime import date
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def get_issue_details_based_on_book_and_user(connection, user_id, book_id):
    cursor = connection.cursor()
    cursor.callproc('get_issue_details_based_on_book_and_user', [user_id, book_id])

    if cursor.rowcount != 0:
        for row in cursor.fetchall():
            return {'id': row[0],
                    'book_id': row[2],
                    'borrow_date': json.dumps(row[3], default=str),
                    'default_return_date': json.dumps(row[4], default=str),
                    'actual_return_date': json.dumps(row[5], default=str),
                    'fine': row[6],
                    'status': row[7]
                    }

    return {}


def calculate_fine(expected, actual):
    expected_list = expected.split('-')
    actual_list = str(actual).split('-')

    fine = 0
    expected_year = str(expected_list[0]).replace('\\', '').replace('"', '')
    expected_day = str(expected_list[2]).replace('\\', '').replace('"', '')
    if int(actual_list[0]) == int(expected_year):
        if int(actual_list[1]) == int(expected_list[1]):
            if int(actual_list[2]) > int(expected_day):
                fine = 1 * (int(actual_list[2]) - int(expected_day))

        elif int(actual_list[1]) > int(expected_list[1]):
            fine = 5 * (int(actual_list[1]) - int(expected_list[1]))

    elif int(actual_list[0]) > int(expected_year):
        fine = 1000

    return fine


def handler(event, context):
    connection = None
    try:
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        user_id = event['user_id']
        book_id = event['book_id']
        user_issued_book_details = get_issue_details_based_on_book_and_user(connection, user_id, book_id)

        if user_issued_book_details:
            today = date.today().strftime('%Y-%m-%d')
            fine = calculate_fine(user_issued_book_details['default_return_date'], today)
            event['status'] = 'success'
            event['calculated_fine'] = fine

        else:
            event['status'] = 'fail'
            event['message'] = 'no such book is issued!'

    except Exception as e:
        print("Exception occurred:{}".format(e))
        event['status'] = 'fail'
        event['message'] = format(e)

    finally:
        connection.close()

    return event
