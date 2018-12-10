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

page_size = int(os.getenv('batch_size', '100'))

batch_load_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_load_tmp.sql'
sync_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_sync.sql'
insert_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_insert.sql'
update_sql_path = os.path.dirname(os.path.realpath(__file__)) + '/sql/projects_update.sql'


def sync_batch(dbConn, rows):
    # 

    if dbConn is None:
        raise "Database connection is not open."

    row_template = """
    (%(project_id)s
    ,%(created_at)s
    ,%(modified_at)s
    ,%(state)s
    ,%(marked_for_deletion)s
    ,%(flash_id)s
    ,%(admin_edit_date)s
    ,%(admin_editor)s
    ,%(source_project_id)s
    ,%(customer_id)s
    ,%(sku)s
    ,%(page_count)s
    ,%(photo_boxes)s
    ,%(photo_boxes_complete)s
    ,%(gallery_images_uploaded)s
    ,%(product_attributes)s
    ,%(price)s)
    """

    db.execute_batch_path(dbConn, batch_load_sql_path, rows, row_template, page_size)


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
