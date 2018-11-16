## Docs
### Original Spec Doc
https://docs.google.com/document/d/1u-K2Tw8BbMSmIKrvUf2FL28-txd1y1gtyj0WNiHEtPU/edit?ts=5be9d519#

### Detailed Implementation Doc
https://docs.google.com/document/d/1UguCDXLQa8C3QmdBhd1veqz-zEM_L52uXqfyxm3JVCk/edit#heading=h.7p9acygja0x

## Requirements

* Python 3.6
* nodeJS
* virtualenv
* Docker

### psycopg2
The AWS Lambda python environment doesn't natively come with _libpq.so_ which is necessary to connect to Redshift.  We must manually include a pre-compiled version

https://blog.mitocgroup.com/aws-lambda-to-redshift-connection-using-iam-authentication-and-nat-gateway-b40c6002082b

Download from https://github.com/jkehler/awslambda-psycopg2


## Install Instructions

* npm install -g serverless
* git clone <repo>
* cd <repo>
* virtualenv venv --python=python3.6
* source venv/bin/activate
* npm i serverless-python-requirements
* pip install -r requirements.txt
* sls deploy

## Artifact Uprising Configuration
The current confiruation is set to the Mammoth Growth dev environment.  _serverless.yml_ should be updated to reflect Artifact Uprising's environment.

``` yaml
provider:
  name: aws
  runtime: python3.6
  stage: dev
  region: us-west-2
  profile: mammothgrowth
  timeout: 300
  environment:
    dynamo_table_projects: ${self:custom.tableNames.projects}
    redshift_url: artifact-2.cf5wz3dozczr.us-west-2.redshift.amazonaws.com
    redshift_port: "5439"
    redshift_user: temp_dynamo_sync
    redshift_database: artifact_uprising
    redshift_cluster: artifact-2
    redshift_table_projects: artifact_uprising.project_data
    sqs_queue_projects: DynamoRedshiftSyncQueue
```

#### stage
update the stage to `dev|stage|prod`

Resource names include the stage name

#### profile
update to specify a local aws-cli profile stored in `~/.aws/credentials`.

Comment out to use the `default`

#### redshift_*
Update to specify Artifact Uprising's Redshift details

#### dynamo_table_projects
Update to the correct DynamoDB table that contains the projects data.

``` yaml
  projectsRedshiftSync:
    handler: lambda_redshift_update.handle
    reservedConcurrency: 1
    events: 
      - sqs: 
          batchSize: 10
          arn:
            Fn::GetAtt:
              - RedshiftSyncSQS
              - Arn
    vpc:
      securityGroupIds:        
        - sg-055faf05648def1d9
      subnetIds:
        - subnet-0444e9eb1caa17313
```

#### securityGroupIds
This specifies that the Lambda should execute within a VPC.  This is necessary to connect to the Redshift cluster.  Add the SecurityGroup with routes to the Redshift cluster.

#### subnetIds:
The Lambda needs access to the internet in order to call AWS API's to get temporary security credentials.  If the VPC is set up as a public/private w/ NAT, add the private subnet(s) associated with the NAT.

#### reservedConcurrency
Setting to 1 causes only a single Lambda processor to write to the Redshift cluster.  If the lambda can't keep up with the SQS queue, increase to add more workers.  Having too many connections will have impact Redshift negatively, so use the minimum necessary.

#### batchSize
How many SQS messages are batched.  This can only be a maximum of 10.
