from fastapi import APIRouter
from app.db import table
from app.models import Device

router = APIRouter()

@router.get("/")
def list_devices(user_id: str):
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": f"user#{user_id}", ":sk": "device#"}
    )
    return resp.get("Items", [])

@router.post("/")
def create_device(user_id: str, device: Device):
    item = { "PK": f"user#{user_id}", "SK": f"device#{device.deviceId}", **device.dict() }
    table.put_item(Item=item)
    return {"status": "ok"}

@router.put("/{device_id}")
def update_device(user_id: str, device_id: str, updates: dict):
    key = { "PK": f"user#{user_id}", "SK": f"device#{device_id}" }
    update_expr = "SET " + ", ".join([f"#{k}=:{k}" for k in updates])
    expr_attr_names = {f"#{k}": k for k in updates}
    expr_attr_vals = {f":{k}": v for k, v in updates.items()}
    table.update_item(Key=key, UpdateExpression=update_expr,
                      ExpressionAttributeNames=expr_attr_names,
                      ExpressionAttributeValues=expr_attr_vals)
    return {"status": "updated"}

@router.delete("/{device_id}")
def delete_device(user_id: str, device_id: str):
    key = { "PK": f"user#{user_id}", "SK": f"device#{device_id}" }
    table.delete_item(Key=key)
    return {"status": "deleted"}
