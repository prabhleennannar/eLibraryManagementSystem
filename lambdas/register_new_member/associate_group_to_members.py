import boto3
import os

client = boto3.client('cognito-idp')
user_pool_id = os.environ['user_pool_id']


def handler(event, context):
    status = event['status']

    if status == 'success':
        user_name = event['user_name']
        group_name = str(event['requested_group']).upper()

        response = client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=user_name,
            GroupName=group_name
        )

    return event
