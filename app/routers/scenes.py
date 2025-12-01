
from fastapi import APIRouter, Depends
from app.auth import verify_jwt
from app.models import SceneModel
from app.dynamo import put_item, get_items_by_prefix

router = APIRouter()

@router.get("/scenes")
def list_scenes(user_id: str = Depends(verify_jwt)):
    return get_items_by_prefix(user_id, "scene#")

@router.post("/scenes")
def add_scene(scene: SceneModel, user_id: str = Depends(verify_jwt)):
    item = {
        "PK": f"user#{user_id}",
        "SK": f"scene#{scene.id}",
        **scene.dict()
    }
    put_item(item)
    return {"status": "scene added"}
