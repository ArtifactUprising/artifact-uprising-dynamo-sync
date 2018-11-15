import boto3
import os
# from botocore.exceptions import ResourceNotFoundException

app_name = 'artifact-uprising-dynamo-sync'

backfill_last_project = "backfill_last_project"

if os.environ.get('IS_LOCAL') == 'true' or __name__ == '__main__':
    print("using local secrets access")
    session = boto3.session.Session(profile_name='mammothgrowth')
    stage = "LOCAL"
    client = session.client('ssm')

else:
    print("using execution context for secrets access")
    stage = "PROD"
    client = boto3.client('ssm')


def __get_secret(environment, key_type):

    secret_key = "/%s/%s/%s" %(app_name, environment, key_type)

    print("Looking up %s" % secret_key)

    try:

        response = client.get_parameter(Name=secret_key, WithDecryption=True)

        # print(response)

        return response['Parameter']['Value']

    except client.exceptions.ParameterNotFound:
        print("Not Found")
        return None

def __set_secret(environment, key_type, secret_string):

    secret_key = "/%s/%s/%s" %(app_name, environment, key_type)

    client.put_parameter(
        Name=secret_key,
        Value=secret_string,
        Type="SecureString",
        Overwrite=True
        # VersionStages=[stage]        
    )

def __remove_secret(environment, key_type):

    secret_key = "/%s/%s/%s" %(app_name, environment, key_type)

    client.delete_parameter(
        Name=secret_key
    )

def get_last_project_id():

    return __get_secret(stage, backfill_last_project)

def set_last_project_id(project_id):

    return __set_secret(stage, backfill_last_project, project_id)

if __name__ == '__main__':
    project_id = get_last_project_id()
    print("Project Id: %s" % project_id)

    set_last_project_id("project id 123")

    project_id = get_last_project_id()
    print("Project Id: %s" % project_id)
