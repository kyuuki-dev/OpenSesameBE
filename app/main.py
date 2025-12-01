from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import boto3
import os
import uuid

app = FastAPI()
security = HTTPBearer()

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = "SesameSmartHome"
table = dynamodb.Table(TABLE_NAME)

# ⚠️ WARNING: For prod, use real Auth0 public key to verify signature
def get_user_id(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, options={"verify_signature": False})
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

@app.get("/devices")
def get_devices(user_id: str = Depends(get_user_id)):
    response = table.query(
        KeyConditionExpression='pk = :uid AND begins_with(sk, :dev)',
        ExpressionAttributeValues={
            ':uid': user_id,
            ':dev': 'DEVICE#'
        }
    )
    return response.get("Items", [])

@app.post("/devices")
def create_device(device: dict, user_id: str = Depends(get_user_id)):
    device_id = str(uuid.uuid4())
    item = {
        'pk': user_id,
        'sk': f'DEVICE#{device_id}',
        'deviceId': device_id,
        'friendlyName': device['friendlyName'],
        'deviceType': device['deviceType'],
        'state': 'OFF'
    }
    table.put_item(Item=item)
    return {"status": "ok", "deviceId": device_id}

@app.post("/devices/{device_id}/control")
def toggle_device(device_id: str, user_id: str = Depends(get_user_id)):
    key = {'pk': user_id, 'sk': f'DEVICE#{device_id}'}
    res = table.get_item(Key=key)
    if 'Item' not in res:
        raise HTTPException(status_code=404, detail="Device not found")

    device = res['Item']
    new_state = "ON" if device["state"] == "OFF" else "OFF"
    device["state"] = new_state

    table.put_item(Item=device)
    return {"status": "toggled", "newState": new_state}

@app.delete("/devices/{device_id}")
def delete_device(device_id: str, user_id: str = Depends(get_user_id)):
    key = {'pk': user_id, 'sk': f'DEVICE#{device_id}'}
    table.delete_item(Key=key)
    return {"status": "deleted"}
