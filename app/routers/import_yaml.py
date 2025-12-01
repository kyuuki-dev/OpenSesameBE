
from fastapi import APIRouter, Depends, UploadFile, File
from app.auth import verify_jwt
from app.models import DeviceModel, SceneModel
from app.dynamo import put_item
import yaml

router = APIRouter()

@router.post("/import-yaml")
async def import_yaml(file: UploadFile = File(...), user_id: str = Depends(verify_jwt)):
    raw = await file.read()
    try:
        data = yaml.safe_load(raw)
        devices = data.get("devices", [])
        scenes = data.get("scenes", [])

        for d in devices:
            dev = DeviceModel(**d)
            put_item({"PK": f"user#{user_id}", "SK": f"device#{dev.id}", **dev.dict()})

        for s in scenes:
            scn = SceneModel(**s)
            put_item({"PK": f"user#{user_id}", "SK": f"scene#{scn.id}", **scn.dict()})

        return {"status": "imported", "devices": len(devices), "scenes": len(scenes)}
    except Exception as e:
        return {"error": str(e)}
