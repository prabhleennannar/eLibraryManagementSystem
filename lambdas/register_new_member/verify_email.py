import boto3

client = boto3.client('ses')


def handler(event, context):
    status = event['status']

    if status == 'success':
        email = event['email']

        response = client.verify_email_identity(
            EmailAddress=email
        )
        event['email_sent_for_verification'] = True

    return event
