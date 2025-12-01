from fastapi import FastAPI, Depends, HTTPException
import boto3
import uuid
from boto3.dynamodb.conditions import Key

app = FastAPI()

# DynamoDB config – set region/env the same way you do locally
dynamodb = boto3.resource("dynamodb")  # or resource("dynamodb", region_name="us-east-1")
TABLE_NAME = "SesameSmartHome"
table = dynamodb.Table(TABLE_NAME)

# -------------------------------------------------
# Auth stub: single demo user, no Auth0/JWT needed
# -------------------------------------------------
DEMO_USER_ID = "demo-user"

def get_user_info():
    """
    No real authentication. Always return the same demo user.
    Frontend does not send any Authorization header.
    """
    return {
        "sub": DEMO_USER_ID,
        "email": None,
        "name": "Demo User",
    }

# -------------------------------------------------
# Endpoints
# -------------------------------------------------

@app.post("/init")
def init_user(user=Depends(get_user_info)):
    user_id = user["sub"]
    profile_key = {"pk": user_id, "sk": "PROFILE#default"}
    res = table.get_item(Key=profile_key)

    if "Item" not in res:
        table.put_item(
            Item={
                "pk": user_id,
                "sk": "PROFILE#default",
                "created": True,
                "email": user.get("email"),
                "name": user.get("name"),
            }
        )

    return {"status": "initialized"}

@app.get("/devices")
def get_devices(user=Depends(get_user_info)):
    user_id = user["sub"]

    # Use proper DynamoDB expression objects, not a raw string:
    response = table.query(
        KeyConditionExpression=Key("pk").eq(user_id) & Key("sk").begins_with("DEVICE#")
    )
    return response.get("Items", [])

@app.post("/devices")
def create_device(device: dict, user=Depends(get_user_info)):
    """
    device = { "friendlyName": "...", "deviceType": "LOCK" | "LIGHT" | ... }
    """
    user_id = user["sub"]
    device_id = str(uuid.uuid4())
    item = {
        "pk": user_id,
        "sk": f"DEVICE#{device_id}",
        "deviceId": device_id,
        "friendlyName": device["friendlyName"],
        "deviceType": device["deviceType"],
        "state": "OFF",
    }
    table.put_item(Item=item)
    return {"status": "ok", "deviceId": device_id}

@app.post("/devices/{device_id}/control")
def toggle_device(device_id: str, user=Depends(get_user_info)):
    user_id = user["sub"]
    key = {"pk": user_id, "sk": f"DEVICE#{device_id}"}
    res = table.get_item(Key=key)
    if "Item" not in res:
        raise HTTPException(status_code=404, detail="Device not found")

    device = res["Item"]
    new_state = "ON" if device["state"] == "OFF" else "OFF"
    device["state"] = new_state

    table.put_item(Item=device)
    return {"status": "toggled", "newState": new_state}

@app.delete("/devices/{device_id}")
def delete_device(device_id: str, user=Depends(get_user_info)):
    user_id = user["sub"]
    key = {"pk": user_id, "sk": f"DEVICE#{device_id}"}
    table.delete_item(Key=key)
    return {"status": "deleted"}
