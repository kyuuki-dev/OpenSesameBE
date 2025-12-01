from pydantic import BaseModel
from typing import List, Optional

class Device(BaseModel):
    deviceId: str
    friendlyName: str
    type: str
    lockState: Optional[str] = "LOCKED"

class SceneAction(BaseModel):
    deviceId: str
    action: str

class Scene(BaseModel):
    sceneId: str
    friendlyName: str
    actions: List[SceneAction]
