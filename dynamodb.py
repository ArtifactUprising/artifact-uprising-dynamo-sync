import boto3
import simplejson as json
import os
import decimal
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, date, timedelta
from dateutil import parser

import logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

if os.environ.get('IS_LOCAL') == 'true' or __name__ == '__main__':
    logger.info("using local Dynamo access")
    session = boto3.session.Session(profile_name='mammothgrowth')
    db = session.resource('dynamodb')
    projects_table_name = "artifact-uprising-projects-2-dev"

else:
    logger.info("using execution context for Dynamo access")
    db = boto3.resource('dynamodb')

    projects_table_name = os.environ.get('dynamo_table_projects')

projects_table = db.Table(projects_table_name)

def get_projects(limit):
        
        response = projects_table.scan(
            Limit=limit
        )

        response = projects_table.scan()

        yield response['Items']

        while 'LastEvaluatedKey' in response:
            response = projects_table.scan(
                Limit=limit,
                ExclusiveStartKey=response['LastEvaluatedKey']
                )

            yield response['Items']


if __name__ == "__main__":
    
    for projects in get_projects(2):
        for project in projects:
            print(project['projectId'])

    # if projects and len(projects) > 0:

    #     print("%s projects returned" % len(projects))
    #     print("last projectId: %s" % projects[-1]["projectId"])
    # else:
    #     print("no projects returned")