import json
import logging
import os
import projects_database as db

logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

user = os.getenv('redshift_user')
pwd = os.getenv('redshift_password', None)
database = os.getenv('redshift_database')
cluster = os.getenv('redshift_cluster', None)
port = os.getenv('redshift_port')
endpoint = os.getenv('redshift_url')

def get_records(event):

    records = event['Records']
    
    return [json.loads(i['body']) for i in records]


def handle(event, context):
    
    # logger.debug(json.dumps(event))

    records = get_records(event)

    logger.debug("decoded %s records" % len(records))

    for record in records:
        logger.debug("updating: %s", json.dumps(record))
        update_record(record)


def update_record(record):
    conn = None

    try:
        conn = db.open_database(user, pwd, database, cluster, port, endpoint)

        db.sync_row(conn, record)

    finally:
        if conn:
            db.close_database(conn)
    