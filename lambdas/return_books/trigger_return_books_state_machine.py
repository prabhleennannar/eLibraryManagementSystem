import boto3
import os
import json
import time

cognito_client = boto3.client('cognito-idp')
user_pool_id = os.environ['user_pool_id']

sf_client = boto3.client('stepfunctions')
step_function_arn = os.environ['step_function_arn']


def handler(event, context):
    body = str(event['body']).replace('\n', '')
    json_body = json.loads(body)

    username = json_body.get('username')
    books_list = json_body.get('books_list')

    cognito_response = {}
    if username is None or books_list is None or not books_list:
        response = {
            'status': 'fail',
            'message': '"username" and "books_list" should not be empty!',
            'requested_details': json_body
        }
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }

    else:
        try:
            cognito_response = cognito_client.admin_get_user(
                UserPoolId=user_pool_id,
                Username=username
            )

        except cognito_client.exceptions.UserNotFoundException as e:
            response = {
                'status': 'fail',
                'message': 'Either username is incorrect or User is not registered yet!',
                'requested_details': json_body
            }
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps(response)
            }

    user_attributes = cognito_response.get('UserAttributes')
    user_id = None
    username = None

    for user_attribute in user_attributes:
        if user_attribute.get('Name') == 'sub':
            user_id = user_attribute.get('Value')
        if user_attribute.get('Name') == 'name':
            username = user_attribute.get('Value')

    books_list = json_body['books_list']
    return_request = []
    for book_id in books_list:
        return_request.append({
            'book_id': book_id,
            'user_id': user_id
        })

    sf_input = {
        'email': json_body['username'],
        'books_list': books_list,
        'user_id': user_id,
        'username': username,
        'return_request': return_request
    }
    sf_response = sf_client.start_execution(
        stateMachineArn=step_function_arn,
        input=json.dumps(sf_input)
    )
    execution_arn = sf_response['executionArn']
    time.sleep(5)
    sf_execution_response = sf_client.describe_execution(
        executionArn=execution_arn
    )
    output = sf_execution_response['output']
    print(output)

    if output is not None:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": output
        }

    else:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps('Some exception occurred!')
        }
