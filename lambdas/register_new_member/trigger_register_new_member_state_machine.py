import boto3
import os
import json
import time

client = boto3.client('stepfunctions')
step_function_arn = os.environ['step_function_arn']
valid_group = ['admins', 'users']


def handler(event, context):
    print(context)
    print(event)
    body = str(event['body']).replace('\n', '')
    authorizer = event['requestContext']['authorizer']
    group = authorizer.get('group')

    json_body = json.loads(body)
    name = json_body.get('name')
    email = json_body.get('email')
    requested_group = json_body.get('group')

    if name is None or len(name) == 0 or email is None or len(email) == 0 or requested_group is None or \
            len(requested_group) == 0:
        response = {
            'status': 'fail',
            'message': 'Either of name, email, group should not be empty!',
            'requested_details': json_body
        }
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }

    if str(requested_group).lower() not in valid_group:
        response = {
            'status': 'fail',
            'message': 'Please enter value group name: admins or users!',
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
        'email': email,
        'name': name,
        'requested_group': str(requested_group).upper(),
        'group': group
    }

    sf_response = client.start_execution(
        stateMachineArn=step_function_arn,
        input=json.dumps(sf_input)
    )

    execution_arn = sf_response['executionArn']

    time.sleep(5)
    sf_execution_response = client.describe_execution(
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
