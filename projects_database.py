"""
    encapsulates logic for updating specific Redshift table.  
        opens DB connection
        checks for existence
        performs upsert

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import redshift as db
import sys
import os
import logging

logger = logging.getLogger()
logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

sync_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_sync.sql'
insert_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_insert.sql'
update_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_update.sql'

def sync_row(dbConn, row):
    if 'project_id' not in row:
        raise "Missing id value."

    if dbConn is None:
        raise "Database connection is not open."

    sync_result = db.execute_path(dbConn, sync_sql_path, row, True)

    if sync_result is None:
        logger.info("inserting")
        db.execute_path(dbConn, insert_sql_path, row)
        return
    else:
        logger.info("updating")        
        db.execute_path(dbConn, update_sql_path, row)
        return

def open_database(user, pwd, database, cluster, port, endpoint):

    return db.open_connection_secure(user, database, cluster, port, endpoint)

def close_database(dbConn):

    db.close_connection(dbConn)
