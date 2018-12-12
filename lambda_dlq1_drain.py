"""
    Lambda handler / entry point.  
        Drains the original DLQ which contain the flat updates
        Note, this is not able to drain the new Kinesis DLQ 

        Dequeues from SQS and sends to Kinesis stream

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import json
import logging
import os
import base64
import kinesis_send

logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

kinesis_queue = os.getenv('kinesis_queue_projects', 'ProjectsDynamoDBRedshiftSync')

def parse_record(record):

    # SQS record
    if 'body' in record:
        return json.loads(record['body'])
    # Kinesis record
    elif 'kinesis' in record:
        data = base64.b64decode(record['kinesis']['data'])
        return json.loads(data)
    else:
        return None

def get_records(event):

    records = event['Records']
     
    return [parse_record(i) for i in records]


def handle(event, context):
    
    records = get_records(event)

    logger.debug("decoded %s records" % len(records))

    projectids = [i['project_id'] for i in records]
    
    logger.info("processing projects: %s" % projectids)

    update_batch(records)

def update_batch(records):    

    for record in records:
        project_id = record['project_id']
        kinesis_send.send_message(record, kinesis_queue, project_id)
