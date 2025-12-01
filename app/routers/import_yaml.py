from fastapi import APIRouter, UploadFile, Form
import yaml
from app.db import table

router = APIRouter()

@router.post("/yaml")
async def import_yaml(user_id: str = Form(...), file: UploadFile = Form(...)):
    content = await file.read()
    data = yaml.safe_load(content)
    for device in data.get("devices", []):
        item = {
            "PK": f"user#{user_id}",
            "SK": f"device#{device['id']}",
            "deviceId": device["id"],
            "friendlyName": device["name"],
            "type": device["type"],
            "lockState": device.get("state", {}).get("lockState", "LOCKED")
        }
        table.put_item(Item=item)
    return {"status": "imported", "count": len(data.get("devices", []))}
