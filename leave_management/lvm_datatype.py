from pydantic import BaseModel, validator
from db_management.db_enums import LeaveStatusEnum, LeaveTypeEnum, MeetingEnum, ApproverTypeEnum
from typing import Optional, List
from fastapi import HTTPException
import datetime
from pydantic.config import Extra


class StaffLeaveType(BaseModel):
    leave_type: LeaveTypeEnum
    total_available: float
    description: Optional[str] = ""

    @validator("total_available")
    def validate_available_leaves(cls, value):
        if (value - int(value)) not in [0, 0.5] or value < 0 or value > 366:
            raise HTTPException(422, "total_available not valid.")
        return value


class StudentLeaveType(BaseModel):
    leave_type: LeaveTypeEnum
    description: Optional[str] = ""


class AdminLeaveConfigDataType(BaseModel):
    id: int
    staff_leaves: List[StaffLeaveType]
    student_leaves: List[StudentLeaveType]


class LeaveTimeDataType(BaseModel):
    date: datetime.date
    meeting: MeetingEnum


class LeaveDetailDataTypeIn(BaseModel):
    leave_start: LeaveTimeDataType
    leave_end: LeaveTimeDataType
    leave_type: LeaveTypeEnum
    description: Optional[str] = ""
    authorizer: ApproverTypeEnum
    docurl: str


class LeaveDataTypeOut(LeaveDetailDataTypeIn):
    leave_id: int
    leave_count: float
    leave_status: LeaveStatusEnum
    reacted_by: Optional[ApproverTypeEnum] = None
    reacted_at: Optional[datetime.datetime] = None


class StudentDataTypeForLeave(BaseModel):
    student_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    picurl: Optional[str] = None

    class Config:
        extra = Extra.ignore


class SectionDataTypeForLeave(BaseModel):
    section_id: int
    school_class_id: int
    class_name: str
    section_name: Optional[str] = None

    class config:
        extra = Extra.ignore


class StaffDataTypeForLeave(BaseModel):
    staff_id: int
    name: str
    pic_url: Optional[str] = None

    class Config:
        extra = Extra.ignore


class StudentLeaveDataTypeOut(BaseModel):
    student: StudentDataTypeForLeave
    leave: LeaveDataTypeOut


class StudentLeaveWithSectionDataTypeOut(BaseModel):
    student: StudentDataTypeForLeave
    section: SectionDataTypeForLeave
    leave: LeaveDataTypeOut


class StaffLeaveDataTypeOut(BaseModel):
    staff: StaffDataTypeForLeave
    leave: LeaveDataTypeOut
