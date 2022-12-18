from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Optional
from pydantic import validator

class UserLoginIN(BaseModel):
    username: str
    password: str
    
class UserCreateDataTypeIn(BaseModel):
    username: str
    password_1: str
    password_2: str

    @validator('password_1')
    def password_validate(cls, v):
        assert len(v) >= 8, 'password must be at least 8 chars long.'
        assert not v.isnumeric(), 'password must contain at least one alphabet.'
        return v

    @validator('password_2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password_1' in values and v != values['password_1']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

class UserDataType(BaseModel):
    user_id: int
    username: str
    active: bool

class DesignationDataTypeOutForAuth(BaseModel):
    designation_id: int
    designation: str
    role: str
    role_instance_id: int
    permission_json: Dict = {} #This is the default. Handle in later when project grows.