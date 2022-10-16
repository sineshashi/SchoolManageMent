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

class UserCreateDataTypeIn(BaseModel):
    username: str
    password1: str
    password2: str

    @validator('password1')
    def password_validate(cls, v):
        assert len(v) >= 8, 'password must be at least 8 chars long.'
        assert not v.isnumeric(), 'password must contain at least one alphabet.'
        return v

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v