from pydantic import BaseModel
from typing import Optional
from pydantic import validator

class UserLoginIN(BaseModel):
    username: str
    password: str
    
class DeviceIN(BaseModel):
    device_model: str = ""
    platform: str = ""
    os_version: str = ""
    operating_system: str = ""
    manufacturer: str = ""
    browser_name: str = ""
    device_location: Optional[str] = None