import boto3
import simplejson as json
import os
import decimal
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, date, timedelta
from dateutil import parser

if os.environ.get('IS_LOCAL') == 'true' or __name__ == '__main__':
    print("using local Dynamo access")
    session = boto3.session.Session(profile_name='mammothgrowth')
    db = session.resource('dynamodb')
    projects_table_name = "artifact-uprising-projects-dev"

else:
    print("using execution context for Dynamo access")
    db = boto3.resource('dynamodb')

    projects_table_name = os.environ.get('dynamo_table_projects')
projects_table = db.Table(projects_table_name)

def get_projects(last_project_id, limit):

    if last_project_id:
    
        ke = Key('project_id').gt(last_project_id)

        response = projects_table.query(
            KeyConditionExpression=ke,
            Limit=limit
        )

    else:
        response = projects_table.scan(
            Limit=limit
        )

    all_projects = response['Items']

    return all_projects

if __name__ == "__main__":
    projects = get_projects(None, 10)

    if projects and len(projects) > 0:

        print("%s projects returned" % len(projects))
        print("last project_id: %s" % projects[-1]["project_id"])
    else:
        print("no projects returned")