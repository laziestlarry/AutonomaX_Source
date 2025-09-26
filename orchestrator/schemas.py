
from pydantic import BaseModel
from typing import Dict, Any

class Task(BaseModel):
    type: str
    payload: Dict[str, Any]
