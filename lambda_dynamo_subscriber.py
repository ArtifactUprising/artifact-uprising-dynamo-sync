import json
import logging
import os
import projects_mapping as mapper
import sqs_send as sqs

logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

sqs_queue = os.getenv('sqs_queue_projects', 'DynamoRedshiftSyncQueue')

def get_records(event):

    records = event['Records']
    
    return [i['dynamodb']['NewImage'] for i in records if i['eventName'] in ['INSERT', 'MODIFY']]

def map(record):

    return mapper.map(mapper.flatten_dynamo_document(record))

def handle(event, context):
    
    logger.debug(json.dumps(event))

    records = get_records(event)

    mapped = [map(record) for record in records]

    sent = []
    for message in filter(lambda x: x['project_id'], mapped):
        sqs.send_message(message, sqs_queue)
        sent.append(message['project_id'])

    response = {
        "statusCode": 200,
        "body": json.dumps(sent)
    }

    return response
