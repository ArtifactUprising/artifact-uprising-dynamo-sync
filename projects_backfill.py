"""
    manual backfill script.  
        enumerates through every DynamoDB document
        maps document into redshift update
        queues update onto SQS

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import os
if __name__ == '__main__':
    os.environ['IS_LOCAL'] = 'true'
import dynamodb
import projects_mapping as mapper
import sqs_send as sqs
import logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'INFO'))

sqs_queue = os.getenv('sqs_queue_projects', 'DynamoRedshiftSyncQueue')

limit = 1

def map(record):

    return mapper.map(record)

def backfill():

    sent = []

    for records in dynamodb.get_projects(limit):

        for mapped in [map(record) for record in records]:
            print("sending: %s" % mapped['project_id'])
            sent.append(mapped['project_id'])
            sqs.send_message(mapped, sqs_queue)

    print("sent: %s" % sent)

if __name__ == '__main__':

    backfill()
