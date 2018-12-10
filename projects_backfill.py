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
import kinesis_send as kinesis
import logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'INFO'))

kinesis_queue = os.getenv('kinesis_queue_projects', 'ProjectsDynamoDBRedshiftSync')

limit = 1

def map(record):

    return mapper.map(record, True)

def backfill():

    sent = []

    for records in dynamodb.get_projects(limit):

        for mapped in [map(record) for record in records]:
            # for i in [0,1,2,3,4]:

            project_id = mapped['project_id']
            print("sending: %s" % mapped)
            sent.append(project_id)
            kinesis.send_message(mapped, kinesis_queue, project_id)



if __name__ == '__main__':

    backfill()
