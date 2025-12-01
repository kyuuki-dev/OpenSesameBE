
from fastapi import APIRouter, Depends
from app.auth import verify_jwt
from app.models import DeviceModel
from app.dynamo import put_item, get_items_by_prefix

router = APIRouter()

@router.get("/devices")
def list_devices(user_id: str = Depends(verify_jwt)):
    return get_items_by_prefix(user_id, "device#")

@router.post("/devices")
def add_device(device: DeviceModel, user_id: str = Depends(verify_jwt)):
    item = {
        "PK": f"user#{user_id}",
        "SK": f"device#{device.id}",
        **device.dict()
    }
    put_item(item)
    return {"status": "device added"}
