import boto3
import os

import botocore.exceptions

client = boto3.client('cognito-idp')
user_pool_id = os.environ['user_pool_id']


def handler(event, context):
    print(event)
    print('inside Create New User')
    name = event['name']
    email = event['email']

    try:
        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'name',
                    'Value': name
                },
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ],
            ForceAliasCreation=False,
            DesiredDeliveryMediums=[
                'EMAIL',
            ]
        )

        event['message'] = 'User Created Successfully!'
        event['status'] = 'success'
        event['user_name'] = response['User']['Username']
        return event

    except client.exceptions.UsernameExistsException as e:
        event['message'] = 'Username already exists!'
        event['status'] = 'fail'
        return event

    except botocore.exceptions.ClientError as e:
        event['message'] = str(e)
        event['status'] = 'fail'
        return event

