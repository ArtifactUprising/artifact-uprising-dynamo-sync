#!/usr/bin/python3

"""
    encapsulates raw Redshift connection/execution.  
        IAM role based authentication
        Execute raw SQL or local SQL file.
        pattern/replace SQL with input

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import psycopg2
import boto3
import os

if os.environ.get('IS_LOCAL') == 'true' or __name__ == '__main__':
    print("using local Redshift access")
    session = boto3.session.Session(profile_name='mammothgrowth')
    client = session.client('redshift')

else:
    print("using execution context for Dynamo access")
    client = boto3.client('redshift')

def execute(conn, sql, query_params, returnvalue=False):
    """ Connect to the PostgreSQL database server """
    try:
        # create a cursor
        cur = conn.cursor()

        thesql = sql % query_params
        print("Executing:")
        print(thesql)
        
        # execute a statement
        cur.execute(sql, query_params)

        if returnvalue:
            # display the PostgreSQL database server version
            results = cur.fetchone()
            cur.close()
            return results
        else:
            cur.close()
            pass
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

def execute_path(conn, sql_path, query_params, returnvalue=False):
    with open(sql_path, 'r') as sql_file:
      etl_sql = sql_file.read()
      return execute(conn, etl_sql, query_params, returnvalue)

def open_connection_secure(user, database, cluster, port, endpoint):
    print("client: %s" % client)
    creds = client.get_cluster_credentials(
        DbUser=user,
        DbName=database,
        ClusterIdentifier=cluster,
        DurationSeconds=3600)

    print("credentials %s" % creds)

    conn = psycopg2.connect(
        dbname=database,
        user=creds['DbUser'],
        password=creds['DbPassword'],
        port=port,
        host=endpoint)

    conn.autocommit = True
    return conn

def open_connection(user, pwd, database, port, endpoint):

    conn_string = "dbname=%s user=%s password=%s host=%s port=%s"  %(database, user, pwd, endpoint, port)
    # print("conn string: %s" % conn_string)
    conn = psycopg2.connect(conn_string)

    conn.autocommit = True
    return conn

def close_connection(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')
