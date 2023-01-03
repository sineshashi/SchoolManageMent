from fastapi import APIRouter, Body, Depends
from .hlm_logic import AdminHolidayManager, SectionHolidayManager, HolidayTypes
from db_management.db_enums import DayEnum
from permission_management.base_permission import union_of_all_permission_types
from permission_management.holiday_permissions import can_add_holiday, can_view_holiday
from .hlm_datatypes import (WeeklyHolidayDataTypeOut, AnnualHolidayDataTypeOut,
                            IrregualHolidayDataTypeOut, AllHolidaysDataTypeOut, AllHolidaysDataTypeOutForSection,
                            IrregualHolidayDataTypeOutForSection)
import datetime
from typing import Optional, List
from project.shared.common_datatypes import SuccessReponse

router = APIRouter()


@router.post("/createNewWeeklyHoliday", response_model=WeeklyHolidayDataTypeOut)
async def create_new_weekly_holiday(
    day: DayEnum = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday_manager = AdminHolidayManager(
        admin_id=admin_id, semester_id=semester_id)
    return await holiday_manager.create_weekly_holiday(day=day, updated_by_id=token_data.user_id)


@router.post("/createNewAnnualHoliday", response_model=AnnualHolidayDataTypeOut)
async def create_new_annual_holiday(
    date: datetime.date = Body(embed=True),
    title: str = Body(embed=True),
    description: Optional[str] = Body(default=None, embed=True),
    picurl: Optional[str] = Body(default=None, embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday_manager = AdminHolidayManager(admin_id, semester_id)
    return await holiday_manager.create_annual_holiday(
        title, date, token_data.user_id, description, picurl
    )


@router.post("/createNewOtherHoliday", response_model=IrregualHolidayDataTypeOut)
async def create_new_annual_holiday(
    start_date: datetime.date = Body(embed=True),
    end_date: datetime.date = Body(embed=True),
    title: str = Body(embed=True),
    description: Optional[str] = Body(default=None, embed=True),
    picurl: Optional[str] = Body(default=None, embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    section_ids: List[int] = Body(default=[], embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday_manager = AdminHolidayManager(admin_id, semester_id)
    return await holiday_manager.create_irregular_holiday(
        title, start_date, end_date, token_data.user_id, description, picurl, section_ids
    )


@router.get("/listAllHolidays", response_model=AllHolidaysDataTypeOut)
async def listAllHolidays(
    admin_id: int,
    semester_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_holiday)
):
    return await AdminHolidayManager(admin_id, semester_id).fetch_all_holidays()


@router.get("/listAllHolidaysForSection", response_model=AllHolidaysDataTypeOutForSection)
async def list_all_holidays_for_section(
    admin_id: int,
    semester_id: int,
    section_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_holiday)
):
    return await SectionHolidayManager(admin_id, semester_id, section_id).fetch_all_holidays()


@router.get("/getWeeklyHoliday", response_model=WeeklyHolidayDataTypeOut)
async def get_weekly_holiday(
    admin_id: int,
    semester_id: int,
    holiday_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_holiday)
):
    holiday = await AdminHolidayManager(
        admin_id, semester_id
    ).get_holiday(HolidayTypes.weekly_holiday_table, holiday_id)
    return WeeklyHolidayDataTypeOut.parse_obj(holiday.dict())


@router.get("/getAnnualHoliday", response_model=AnnualHolidayDataTypeOut)
async def get_weekly_holiday(
    admin_id: int,
    semester_id: int,
    holiday_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_holiday)
):
    holiday = await AdminHolidayManager(
        admin_id, semester_id
    ).get_holiday(HolidayTypes.annual_holiday_table, holiday_id)
    return AnnualHolidayDataTypeOut.parse_obj(holiday.dict())


@router.get("/getOtherHoliday", response_model=IrregualHolidayDataTypeOut)
async def get_weekly_holiday(
    admin_id: int,
    semester_id: int,
    holiday_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_holiday)
):
    holiday = await AdminHolidayManager(
        admin_id, semester_id
    ).get_holiday(HolidayTypes.irregular_holiday_table, holiday_id)
    return IrregualHolidayDataTypeOut.parse_obj(holiday.dict())


@router.get("/getOtherHolidayForSection", response_model=IrregualHolidayDataTypeOutForSection)
async def get_weekly_holiday(
    admin_id: int,
    semester_id: int,
    holiday_id: int,
    section_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_holiday)
):
    return await SectionHolidayManager(admin_id, semester_id, section_id).get_irregular_holiday(holiday_id)


@router.put("/updateWeeklyHoliday", response_model=WeeklyHolidayDataTypeOut)
async def update_holiday_weekly_holiday(
    holiday_id: int = Body(embed=True),
    day: DayEnum = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday = await AdminHolidayManager(admin_id, semester_id).update(
        holiday_type=HolidayTypes.weekly_holiday_table,
        holiday_id=holiday_id,
        day=day,
        updated_by_id=token_data.user_id
    )
    return WeeklyHolidayDataTypeOut.parse_obj(holiday.dict())


@router.put("/updateAnnualHoliday", response_model=AnnualHolidayDataTypeOut)
async def update_holiday_annual_holiday(
    holiday_id: int = Body(embed=True),
    date: datetime.date = Body(embed=True),
    title: str = Body(embed=True),
    description: Optional[str] = Body(default=None, embed=True),
    picurl: Optional[str] = Body(default=None, embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday = await AdminHolidayManager(admin_id, semester_id).update(
        holiday_type=HolidayTypes.annual_holiday_table,
        holiday_id=holiday_id,
        date=date,
        title=title,
        description=description,
        picurl=picurl
    )
    return AnnualHolidayDataTypeOut.parse_obj(holiday.dict())


@router.put("/updateOtherHoliday", response_model=IrregualHolidayDataTypeOutForSection)
async def update_holiday_other_holiday(
    holiday_id: int = Body(embed=True),
    start_date: datetime.date = Body(embed=True),
    end_date: datetime.date = Body(embed=True),
    title: str = Body(embed=True),
    description: Optional[str] = Body(default=None, embed=True),
    picurl: Optional[str] = Body(default=None, embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday = await AdminHolidayManager(admin_id, semester_id).update(
        holiday_type=HolidayTypes.irregular_holiday_table,
        holiday_id=holiday_id,
        updated_by_id=token_data.user_id,
        start_date=start_date,
        end_date=end_date,
        description=description,
        picurl=picurl,
        title=title
    )
    return IrregualHolidayDataTypeOutForSection.parse_obj(holiday.dict())


@router.put("/addNewSectionsToOtherHoliday", response_model=IrregualHolidayDataTypeOut)
async def add_new_sections_to_other_holiday(
    holiday_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    section_ids: List[int] = Body(default=[], embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday = await AdminHolidayManager(
        admin_id, semester_id
    ).add_sections_to_irregular_holiday(holiday_id=holiday_id, section_ids=section_ids)
    return IrregualHolidayDataTypeOut.parse_obj(holiday.dict())


@router.put("/removeSectionsFromOtherHoliday", response_model=IrregualHolidayDataTypeOut)
async def remove_sections_from_other_holiday(
    holiday_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    section_ids: List[int] = Body(default=[], embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    holiday = await AdminHolidayManager(
        admin_id, semester_id
    ).remove_sections_from_irregular_holiday(holiday_id=holiday_id, section_ids=section_ids)
    return IrregualHolidayDataTypeOut.parse_obj(holiday.dict())


@router.delete("/discardAnnualHoliday", response_model=SuccessReponse)
async def discard_annual_holiday(
    holiday_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    await AdminHolidayManager(admin_id, semester_id).discard(
        holiday_type=HolidayTypes.annual_holiday_table,
        holiday_id=holiday_id
    )


@router.delete("/discardOtherHoliday", response_model=SuccessReponse)
async def discard_other_holiday(
    holiday_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    await AdminHolidayManager(admin_id, semester_id).discard(
        holiday_type=HolidayTypes.irregular_holiday_table,
        holiday_id=holiday_id
    )


@router.delete("/discardWeeklyHoliday", response_model=SuccessReponse)
async def discard_weekly_holiday(
    holiday_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    semester_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_holiday)
):
    await AdminHolidayManager(admin_id, semester_id).discard(
        holiday_type=HolidayTypes.weekly_holiday_table,
        holiday_id=holiday_id
    )
