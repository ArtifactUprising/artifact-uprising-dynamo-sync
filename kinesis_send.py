"""
    encapsulates Kinesis message posting.  

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import boto3
import simplejson as json
import os


if os.environ.get('IS_LOCAL') == 'true':
    print("using local Kinesis access")
    session = boto3.session.Session(profile_name='mammothgrowth')
    kinesis = session.client('kinesis')
else:
    print("using execution context for Kinesis access")
    kinesis = boto3.client('kinesis')

def send_message(message, queue_name, partition_key):

    message_body = json.dumps(message)

    # print("Sending to Kinesis %s" % queue_name)

    return kinesis.put_record(
        StreamName=queue_name,
        Data=message_body,
        PartitionKey=partition_key        
    )
