import boto3
import os
import json

sqs_url = os.environ['sqsUrl']
sqs = boto3.client('sqs')


def handler(event, context):
    requested_details = event.get('requested_details')
    message = {
        'email': requested_details.get('email'),
        'username': requested_details.get('username'),
        'result': event.get('result'),
        'previous_issued_book_details': event.get('issued_book_details'),
        'email_type': 'issue'
    }

    sqs.send_message(
        QueueUrl=sqs_url,
        MessageBody=json.dumps(message)
    )

    event['is_mail_sent'] = True
    return event
