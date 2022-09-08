from project.models import Designation, UserDB
from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import pydantic_model_creator

userDataTypeIn = pydantic_model_creator(UserDB, exclude_readonly=True)

DesignationDataTypeIn = pydantic_model_creator(
    Designation, exclude_readonly=True)


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
