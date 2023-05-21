import boto3
import os
import json
import time

sf_client = boto3.client('stepfunctions')
step_function_arn = os.environ['step_function_arn']


def handler(event, context):
    body = str(event['body']).replace('\n', '')
    json_body = json.loads(body)

    title = json_body.get('title')
    author = json_body.get('author')
    genre = json_body.get('genre')
    qty = json_body.get('qty')

    if title is None or len(title) == 0 or author is None or len(author) == 0 or genre is None or len(genre) == 0\
            or qty is None:
        response = {
            'status': 'fail',
            'message': 'Either of title, genre, author and qty should not be empty!',
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
        'request': {
            'title': title,
            'author': author,
            'genre': genre,
            'qty': qty
        }
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
