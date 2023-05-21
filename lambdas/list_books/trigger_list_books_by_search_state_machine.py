import boto3
import os
import json
import time

client = boto3.client('stepfunctions')
step_function_arn = os.environ['step_function_arn']


def handler(event, context):
    print(event)
    body = str(event['body']).replace('\n', '')
    json_body = json.loads(body)

    choice = json_body.get('choice')
    if choice is not None and len(choice) != 0:
        if choice == 'title' or choice == 'author' or choice == 'genre':
            name = json_body.get('name')

            if name is None or len(name) == 0:
                response = {
                    'status': 'fail',
                    'message': 'name field should not be empty  when searching book based on title, author or '
                               'genre!',
                    'requested_details': json_body
                }
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": json.dumps(response)
                }

        elif choice == 'all' or choice == 'qty':
            print('Valid choices')

        else:
            response = {
                'status': 'fail',
                'message': 'Please enter a valid choice: all, title, author, genre, qty!',
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
        response = {
            'status': 'fail',
            'message': '"choice" should not be empty!',
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
        'choice': str(json_body['choice']).lower(),
        'name': json_body.get('name')
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
