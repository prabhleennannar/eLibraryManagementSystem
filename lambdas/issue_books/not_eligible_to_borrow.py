def handler(event, context):
    reason = event['reason']

    event['status'] = 'fail'
    if reason == 'over limit':
        event['message'] = 'The user already borrowed maximum of allowed books i.e. 5'

    if reason == 'book already issued':
        event['message'] = 'Some of the requested books are already borrowed by the user!'

    return event
