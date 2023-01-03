from pydantic import BaseModel, validator, Extra
from db_management.db_enums import DayEnum
from typing import Optional, List
import datetime
from fastapi import HTTPException


class WeeklyHolidayDataTypeIn(BaseModel):
    day: DayEnum
    admin_id: int
    semester_id: int
    updated_by_id: Optional[int] = None


class AnnualHolidayDataTypeIn(BaseModel):
    date: datetime.date
    title: str
    description: Optional[str] = None
    picurl: Optional[str] = None
    admin_id: int
    semester_id: int
    updated_by_id: Optional[int] = None


class IrregualHolidayDataTypeIn(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    title: str
    description: Optional[str] = None
    picurl: Optional[str] = None
    admin_id: int
    semester_id: int
    updated_by_id: Optional[int] = None
    section_ids: List[int] = []

    @validator("end_date")
    def validate_start_and_end_dates(cls, v, values, **kwargs):
        if "start_date" not in values or v is None or values["start_date"] is None or \
                values["start_date"] > v:
            raise HTTPException(
                422, "Start Date Must be less than or equal to End Date.")
        return v


class WeeklyHolidayDataTypeOut(BaseModel):
    day: DayEnum
    holiday_id: int
    active: bool
    updated_by_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class AnnualHolidayDataTypeOut(BaseModel):
    date: datetime.date
    title: str
    description: Optional[str] = None
    picurl: Optional[str] = None
    updated_by_id: Optional[int] = None
    holiday_id: int
    active: bool
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class SectionDatatype(BaseModel):
    section_id: int
    section_name: Optional[str] = None
    school_class_id: int
    class_name: str


class IrregualHolidayDataTypeOut(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    title: str
    description: Optional[str] = None
    picurl: Optional[str] = None
    updated_by_id: Optional[int] = None
    sections: List[SectionDatatype] = []
    holiday_id: int
    active: bool
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class IrregualHolidayDataTypeOutForSection(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    title: str
    description: Optional[str] = None
    picurl: Optional[str] = None
    updated_by_id: Optional[int] = None
    holiday_id: int
    active: bool
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        extra = Extra.ignore


class AllHolidaysDataTypeOut(BaseModel):
    weekly_holidays: List[WeeklyHolidayDataTypeOut]
    annual_holidays: List[AnnualHolidayDataTypeOut]
    other_holidays: List[IrregualHolidayDataTypeOut]


class AllHolidaysDataTypeOutForSection(BaseModel):
    weekly_holidays: List[WeeklyHolidayDataTypeOut]
    annual_holidays: List[AnnualHolidayDataTypeOut]
    other_holidays: List[IrregualHolidayDataTypeOutForSection]
