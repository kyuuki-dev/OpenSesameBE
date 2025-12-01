from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.auth import get_token_payload
import boto3
import uuid
from datetime import datetime
import os

app = FastAPI()

# CORS (adjust frontend domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use your frontend domain here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table_name = os.environ.get("DYNAMO_TABLE", "SesameSmartHome")
table = dynamodb.Table(table_name)

# ---- USER ENDPOINT ----
@app.get("/me")
def get_or_create_user(payload=Depends(get_token_payload)):
    user_id = payload["sub"]
    email = payload.get("email", "unknown")

    # Check if user exists
    try:
        res = table.get_item(Key={"PK": user_id, "SK": "PROFILE"})
        if "Item" in res:
            return res["Item"]
    except:
        pass

    # Create user profile
    user = {
        "PK": user_id,
        "SK": "PROFILE",
        "email": email,
        "createdAt": datetime.utcnow().isoformat(),
    }
    table.put_item(Item=user)
    return user


# ---- DEVICES ----

@app.get("/devices")
def list_devices(payload=Depends(get_token_payload)):
    user_id = payload["sub"]
    res = table.query(
        KeyConditionExpression="PK = :pk and begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": user_id, ":sk": "DEVICE#"}
    )
    return [
        {
            "deviceId": item["SK"].split("#")[1],
            "friendlyName": item["friendlyName"],
            "deviceType": item["deviceType"],
            "state": item.get("state", "OFF")
        } for item in res.get("Items", [])
    ]


@app.post("/devices")
def add_device(data: dict, payload=Depends(get_token_payload)):
    user_id = payload["sub"]
    device_id = str(uuid.uuid4())
    item = {
        "PK": user_id,
        "SK": f"DEVICE#{device_id}",
        "deviceId": device_id,
        "friendlyName": data["friendlyName"],
        "deviceType": data["deviceType"],
        "state": "OFF",
        "createdAt": datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return {"status": "ok", "deviceId": device_id}


@app.post("/devices/{device_id}/control")
def toggle_device(device_id: str, payload=Depends(get_token_payload)):
    user_id = payload["sub"]
    key = {"PK": user_id, "SK": f"DEVICE#{device_id}"}
    item = table.get_item(Key=key).get("Item")

    if not item:
        raise HTTPException(status_code=404, detail="Device not found")

    new_state = "OFF" if item.get("state") == "ON" else "ON"
    item["state"] = new_state
    table.put_item(Item=item)
    return {"status": "ok", "newState": new_state}


@app.delete("/devices/{device_id}")
def delete_device(device_id: str, payload=Depends(get_token_payload)):
    user_id = payload["sub"]
    key = {"PK": user_id, "SK": f"DEVICE#{device_id}"}
    table.delete_item(Key=key)
    return {"status": "deleted"}


# ---- SCENES (placeholder) ----
@app.get("/scenes")
def get_scenes(payload=Depends(get_token_payload)):
    return [{"id": "scene1", "name": "Sample Scene"}]
