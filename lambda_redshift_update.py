"""
    Lambda handler / entry point.  
        Subscribes to SQS messgaes 
        extracts update
        passes update to projects_database module

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import json
import logging
import os
import projects_database as db
import base64
import sqs_send

logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

user = os.getenv('redshift_user')
pwd = os.getenv('redshift_password', None)
database = os.getenv('redshift_database')
cluster = os.getenv('redshift_cluster', None)
port = os.getenv('redshift_port')
endpoint = os.getenv('redshift_url')

dlq_sqs_queue_name = os.getenv('redshiftSyncDLQName', 'DynamoRedshiftSyncQueueDeadLetter')

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
    
    # logger.debug(json.dumps(event))

    records = get_records(event)

    logger.debug("decoded %s records" % len(records))

    projectids = [i['project_id'] for i in records]
    logger.info("processing projects: %s" % projectids)

    update_batch(records)
    # for record in records:
    #     logger.debug("updating: %s", json.dumps(record))
    #     update_record(record)

def update_batch(records):
    conn = None

    try:
        conn = db.open_database(user, pwd, database, cluster, port, endpoint)        
        logger.debug("perfrming batch update.")
        db.sync_batch(conn, records)
    except Exception as e:
        error_message = str(e)
        
        logger.exception("Error sycning batch.  Sending batch to DLQ: %s" % dlq_sqs_queue_name)

        error_payload = {
            "error_message": error_message,
            "data": records
        }
        sqs_send.send_message(error_payload, dlq_sqs_queue_name)
    finally:
        if conn:
            db.close_database(conn)
    

def update_record(record):
    conn = None

    try:
        conn = db.open_database(user, pwd, database, cluster, port, endpoint)

        db.sync_row(conn, record)

    finally:
        if conn:
            db.close_database(conn)
    