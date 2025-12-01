
import os
import boto3

dynamo = boto3.resource("dynamodb", region_name=os.getenv("DYNAMODB_REGION"))
table = dynamo.Table("VirtualSmartHome")

def put_item(item):
    table.put_item(Item=item)

def get_items_by_prefix(user_id, prefix):
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={":pk": f"user#{user_id}", ":prefix": prefix}
    )
    return response.get("Items", [])
