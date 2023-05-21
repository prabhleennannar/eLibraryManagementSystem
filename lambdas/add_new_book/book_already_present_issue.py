def handler(event, context):
    del event['is_present']
    return event
