from pydantic import BaseModel, validator, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Optional, Union
import datetime
from db_management.models import AcademicSessionAndSemester

class SubjectGroupDepartMentDataType(BaseModel):
    group_name: str
    head_id: Optional[int]=None
    vice_head_id: Optional[int]=None


class SubjectDataType(BaseModel):
    subject_name: str
    head_id: Optional[int]=None
    vice_head_id: Optional[int]=None


class ClassGroupDataType(BaseModel):
    group_name: str
    head_id: Optional[int]=None
    vice_head_id: Optional[int]=None


class ClassDataType(BaseModel):
    class_name: str
    head_id: Optional[int]=None
    vice_head_id: Optional[int]=None
    subject_ids: List[int] = []


class ClassUpdateDataType(BaseModel):
    class_name: str
    head_id: Optional[int]=None
    vice_head_id: Optional[int]=None


class AcademicSessionSemesterDataType(BaseModel):
    '''
    semester_number = 0 means semester is not applicable in the school.
    '''
    academic_session_start_year: int
    academic_session_end_year: int
    semester_number: Optional[int] = 0
    semester_start_date: Optional[datetime.date] = None
    semester_end_date: Optional[datetime.date] = None

    @validator('semester_start_date')
    def validate_semester_date(cls, v, values, **kwargs):
        assert not (v is not None and (
            'semester_number' not in values or values['semester_number'] == 0))
        return v

    @validator('semester_end_date')
    def validate_semester_end_date(cls, v, values, **kwargs):
        assert not (v is not None and (
            'semester_number' not in values or values['semester_number'] == 0 or 'semester_start_date' not in values or values['semester_start_date'] is None))
        return v

class AcademicSessionAndSemesterDataTypeInDB(BaseModel):
    ...

class ClassSectionSemeseterDataType(BaseModel):
    semester_id: Optional[int]=None
    section_name: Optional[str]=None
    class_teacher_id: Union[int, None] = Field(default=None, description='Institute Staff ID of class teacher.')
    vice_class_teacher_id: Union[int, None]=Field(default=None, description='Institute Staff ID of Vice Class Teacher')
    class_monitor_id:Union[int, None]=Field(default=None, description='Student ID of Student.')
    vice_class_monitor_id:Union[int, None]=Field(default=None, description='Student ID of Student.')

class ClassSectionSemesterOutDataType(BaseModel):
    section_id: int
    semester_id: Optional[int]=None
    section_name: Optional[str]=None
    class_teacher_id: Union[int, None] = Field(default=None, description='Institute Staff ID of class teacher.')
    vice_class_teacher_id: Union[int, None]=Field(default=None, description='Institute Staff ID of Vice Class Teacher')
    class_monitor_id:Union[int, None]=Field(default=None, description='Student ID of Student.')
    vice_class_monitor_id:Union[int, None]=Field(default=None, description='Student ID of Student.')
    admin_id: int
    school_class_id: int
    active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    updated_by_id: int = Field(description='user_id of the person who updated it.')

class SubjectAdditionDataType(BaseModel):
    subject_id: int
    subject_teacher_id: int
    assosiate_subject_teacher: Optional[int]=None

class SubjectAdditionOutDataType(BaseModel):
    section_id: int
    subjects: List[SubjectAdditionDataType]=[]

class SectionGetDataType(BaseModel):
    section_id: int
    section_name: Optional[str]=None
    class_teacher_id: Optional[int]=None
    vice_class_teacher_id: Optional[int]=None
    class_monitor_id: Optional[int]=None
    vice_class_monitor_id: Optional[int]=None
    semester_id: Optional[int]=None
    admin_id: int
    school_class_id: int
    active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    updated_by_id: int = Field(description='user_id of the person who updated it.')
    subjects: List[SubjectAdditionDataType]=[]