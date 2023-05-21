import boto3
import os
import json

client = boto3.client('ses')
from_email = os.environ['from_email']


def handler(event, context):
    records = event.get('Records')

    record = records[0]
    body = json.loads(record.get('body'))
    to_email = body.get('email')
    username = body.get('username')

    email_body = body.get('result')
    email_type = body.get('email_type')

    email_subject = None
    if email_type == 'issue':
        email_subject = 'Issued Books Receipt - ' + username + '!'
    if email_type == 'return':
        email_subject = 'Returned Books Receipt - ' + username + '!'

    email_message = {
        'Body': {
            'Text': {
                'Charset': 'utf-8',
                'Data': json.dumps(email_body),
            },
        },
        'Subject': {
            'Charset': 'utf-8',
            'Data': email_subject,
        },
    }

    ses_response = client.send_email(
        Destination={
            'ToAddresses': [to_email],
        },
        Message=email_message,
        Source=from_email
    )

    print(f"ses response id received: {ses_response['MessageId']}.")
