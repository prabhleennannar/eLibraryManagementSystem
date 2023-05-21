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

    books_list = json_body.get('books_list')

    if books_list is None or not books_list:
        response = {
            'status': 'fail',
            'message': '"books_list" should not be empty!',
            'requested_details': json_body
        }
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }

    sf_input = {
        'books_list': json_body['books_list']
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
