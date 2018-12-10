"""
    Lambda handler / entry point.  
        Extracts DynamoDB stream events; 
        flattens document; 
        maps document into data necessary for Redshift update
        posts document onto SQS queue

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import json
import logging
import os
import projects_mapping as mapper
import kinesis_send as kinesis

logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

kinesis_queue = os.getenv('kinesis_queue_projects', 'ProjectsDynamoDBRedshiftSync')

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
        project_id = message['project_id']
        kinesis.send_message(message, kinesis_queue, project_id)
        sent.append(project_id)

    response = {
        "statusCode": 200,
        "body": json.dumps(sent)
    }

    return response
