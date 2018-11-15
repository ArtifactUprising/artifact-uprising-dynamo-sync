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
* sls deploy

## Dev Env
