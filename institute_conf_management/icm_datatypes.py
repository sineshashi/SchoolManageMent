from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

class SubjectGroupDepartMentDataType(BaseModel):
    group_name: str
    head_id: int
    vice_head_id: int

class SubjectDataType(BaseModel):
    subject_name: str
    head_id: int
    vice_head_id: int

class ClassGroupDataType(BaseModel):
    group_name: str
    head_id: int
    vice_head_id: int