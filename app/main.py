from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import boto3
import uuid
import logging

app = FastAPI()
security = HTTPBearer()

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = "SesameSmartHome"
table = dynamodb.Table(TABLE_NAME)

# WARNING: use real public key verification for production
def get_user_info(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, options={"verify_signature": False})
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name")
        }
    except Exception as e:
        logging.error(f"JWT decode failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/init")
def init_user(user = Depends(get_user_info)):
    user_id = user["sub"]
    profile_key = {'pk': user_id, 'sk': 'PROFILE#default'}
    res = table.get_item(Key=profile_key)

    if 'Item' not in res:
        table.put_item(Item={
            'pk': user_id,
            'sk': 'PROFILE#default',
            'created': True,
            'email': user.get("email"),
            'name': user.get("name")
        })

    return {"status": "initialized"}

@app.get("/devices")
def get_devices(user = Depends(get_user_info)):
    user_id = user["sub"]
    response = table.query(
        KeyConditionExpression='pk = :uid AND begins_with(sk, :dev)',
        ExpressionAttributeValues={
            ':uid': user_id,
            ':dev': 'DEVICE#'
        }
    )
    return response.get("Items", [])

@app.post("/devices")
def create_device(device: dict, user = Depends(get_user_info)):
    user_id = user["sub"]
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
def toggle_device(device_id: str, user = Depends(get_user_info)):
    user_id = user["sub"]
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
def delete_device(device_id: str, user = Depends(get_user_info)):
    user_id = user["sub"]
    key = {'pk': user_id, 'sk': f'DEVICE#{device_id}'}
    table.delete_item(Key=key)
    return {"status": "deleted"}
