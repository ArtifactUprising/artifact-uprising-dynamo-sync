import boto3
import simplejson as json
import os

if os.environ.get('IS_LOCAL') == 'true':
    print("using local SQS access")
    session = boto3.session.Session(profile_name='mammothgrowth')
    sqs = session.resource('sqs')
else:
    print("using execution context for SQS access")
    sqs = boto3.resource('sqs')

def send_message(message, queue_name):
    
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    message_body = json.dumps(message)

    print("Sending to queue %s: \n%s" % (queue.url, message_body))

    return queue.send_message(
        MessageBody=message_body
    )