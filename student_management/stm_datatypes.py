from tortoise.contrib.pydantic import pydantic_model_creator
from db_management.models import Student, ParentGaurdian
from pydantic import BaseModel, Extra
from typing import List, Optional, Dict
import datetime
from permission_management.base_permission import StudentPermissionJsonType

StudentDataType = pydantic_model_creator(Student, exclude_readonly=True)
class StudentDataTypeOut(StudentDataType):
    id: int
    father_id: Optional[int]=None
    mother_id: Optional[int]=None
    gaurdian_id: Optional[int]=None
    user_id: int
    admin_id: int
    updated_by_id: Optional[int]

    class Config:
        extra = Extra.ignore

class LogInCredentialsDataType(BaseModel):
    username: str
    password: str

class DesignationDatatype(BaseModel):
    id: int
    designation: str
    role: str
    from_time: Optional[datetime.datetime]=None
    permissions_json: StudentPermissionJsonType

class CreateStudentOutDataType(BaseModel):
    student_data: StudentDataTypeOut
    login_credentials: LogInCredentialsDataType
    section_id: int
    subjects: List[int]=[]
    designation_data: DesignationDatatype

class StudentClassSectionDataType(BaseModel):
    section_id: int
    subject_ids: List[int]=[]

ParentGaurdianDatatype = pydantic_model_creator(ParentGaurdian, exclude_readonly=True)

class ParentGaurdianDataTypeOut(ParentGaurdianDatatype):
    id: int
    updated_by_id: int
    user_id: Optional[int]=None

    class Config:
        extra = Extra.ignore

class ParentGaurdianCreateDataTypeOut(BaseModel):
    parent_data: ParentGaurdianDataTypeOut
    login_credentials: Optional[LogInCredentialsDataType]=None

class ParentGaurdianGetDataTypeOut(ParentGaurdianDatatype):
    id: int
    updated_by_id: int
    user_id: Optional[int]=None
    relation_with_kid: Optional[str]=None

    class Config:
        extra = Extra.ignore

class StudentWithParentDataTypeOut(BaseModel):
    student_data: StudentDataTypeOut
    parent_and_gaurdians: List[ParentGaurdianGetDataTypeOut]=[]

# class ParentGaurdianGetDataTypeOut(BaseModel):
#     __root__: Dict[int, ]