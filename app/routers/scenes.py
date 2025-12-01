from fastapi import APIRouter
from app.db import table
from app.models import Scene

router = APIRouter()

@router.post("/")
def create_scene(user_id: str, scene: Scene):
    item = { "PK": f"user#{user_id}", "SK": f"scene#{scene.sceneId}", **scene.dict() }
    table.put_item(Item=item)
    return {"status": "scene created"}

@router.post("/{scene_id}/execute")
def execute_scene(user_id: str, scene_id: str):
    scene = table.get_item(Key={"PK": f"user#{user_id}", "SK": f"scene#{scene_id}"}).get("Item")
    if not scene:
        return {"error": "Scene not found"}
    for action in scene["actions"]:
        table.update_item(
            Key={"PK": f"user#{user_id}", "SK": f"device#{action['deviceId']}"},
            UpdateExpression="SET lockState = :state",
            ExpressionAttributeValues={":state": action["action"]}
        )
    return {"status": "scene executed"}
