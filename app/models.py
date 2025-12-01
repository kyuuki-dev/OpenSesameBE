
from pydantic import BaseModel
from typing import List, Dict, Optional

class DeviceModel(BaseModel):
    id: str
    name: str
    type: str
    capabilities: List[str]
    state: Optional[Dict[str, str]] = {}

class SceneAction(BaseModel):
    deviceId: str
    command: str
    key: str
    value: str

class SceneModel(BaseModel):
    id: str
    name: str
    actions: List[SceneAction]
