import os
import time
import operator

import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

user_pool_id = os.environ['user_pool_id']
app_client_id = os.environ['client_id']


# For Token validation and policy creation, code is adapted from
# GitHub:
# Availability: https://github.com/Senzing/aws-lambda-cognito-authorizer/blob/main/cognito_authorizer.py
def verify_token(token):
    cognito_user_pool_keys_url = 'https://cognito-idp.us-east-1.amazonaws.com/{}/.well-known/jwks.json' \
        .format(user_pool_id)
    cognito_user_pool_response = requests.get(cognito_user_pool_keys_url).json()
    cognito_user_pool_keys = cognito_user_pool_response['keys']

    jwt_headers = jwt.get_unverified_headers(token)
    kid = jwt_headers['kid']

    found_key = None
    for cognito_user_pool_key in cognito_user_pool_keys:
        if cognito_user_pool_key['kid'] == kid:
            found_key = cognito_user_pool_key

    if found_key is None:
        print('Key found are wrong!')
        return False

    print(found_key)
    jwk_key = jwk.construct(found_key)
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    if not jwk_key.verify(message.encode("utf8"), decoded_signature):
        print("Signature verification failed")
        return False
    print("Signature successfully verified")

    claims = jwt.get_unverified_claims(token)
    print(claims)
    if time.time() > claims['exp']:
        print("Token is expired")
        return False

    if claims['aud'] != app_client_id:
        print("Token was not issued for this audience")
        return False

    return claims


def generate_auth_policy(principal_id, resource, effect):
    auth_response = {"principalId": principal_id}
    if effect and resource:
        policy_document = {"Version": '2012-10-17', "Statement": []}
        statement_one = {"Action": 'execute-api:Invoke', "Effect": effect, "Resource": resource}
        policy_document["Statement"].append(statement_one)
        auth_response["policyDocument"] = policy_document
    return auth_response


def handler(event, context):
    response = {}
    try:
        print(event)
        verification_result = verify_token(event["authorizationToken"])
        resource = event['methodArn']
        if verification_result:
            print("policy is allowed")

            group = verification_result['cognito:groups'][0]
            effect = 'Deny'
            if group == 'ADMINS':
                effect = 'Allow'
            if group == 'USERS':
                if operator.contains(resource, '/user/'):
                    print('User is allowed!')
                    effect = 'Allow'

            response = generate_auth_policy(verification_result['sub'], resource, effect)
            new_context = {
                'sub': verification_result['sub'],
                'group': str(verification_result['cognito:groups'][0]),
                'name': verification_result['name'],
                'email': verification_result['email']
            }
            response['context'] = new_context
            print(response)
        else:
            print("policy is not allowed")
            response = generate_auth_policy(None, resource, 'Deny')

    except Exception as e:
        print(format(e))

    finally:
        return response
