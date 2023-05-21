import boto3
import os
import json

sqs_url = os.environ['sqsUrl']
sqs = boto3.client('sqs')


def handler(event, context):
    message = {
        'email': event.get('email'),
        'username': event.get('username'),
        'result': event.get('result'),
        'issued_book_details': event.get('issued_book_details'),
        'email_type': 'return'
    }

    sqs.send_message(
        QueueUrl=sqs_url,
        MessageBody=json.dumps(message)
    )

    event['is_mail_sent'] = True
    return event
