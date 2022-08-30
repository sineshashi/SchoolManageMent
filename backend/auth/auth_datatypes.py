from pydantic import BaseModel
from typing import Optional
from pydantic import validator

class UserLoginIN(BaseModel):
    username: str
    password: str
    
class DeviceIN(BaseModel):
    device_id: str | None = None
    device_name: str
    browser_name: str
    device_location: Optional[str] = None