import boto3
from botocore.exceptions import ClientError
import json
from dotenv import load_dotenv

def get_secret_from_aws():

    secret_name = "trading_bot/binance_keys"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

def load_secrets():
    if load_dotenv():
        print("Loaded secrets from .env file")
    else:
        print(".env file not found. Attempting to load from AWS Secrets Manager")
        secrets = get_secrets_from_aws()
        for key, value in secrets.items():
            os.environ[key] = value
        print("Loaded secrets from AWS Secrets Manager")