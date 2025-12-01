import boto3
import os

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1'
)

table_name = os.getenv("DYNAMODB_TABLE", "SesameSmartHome")
table = dynamodb.Table(table_name)
