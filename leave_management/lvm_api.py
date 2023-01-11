from fastapi import APIRouter, Body, Depends
from permission_management.leave_permission import can_change_leave_config, can_view_leave_config
from .lvm_logic import AdminLeaveConfigTable, StudentLeaveTable, StaffLeaveTable
from .lvm_datatype import StudentLeaveType, StaffLeaveType, AdminLeaveConfigDataType
from permission_management.base_permission import union_of_all_permission_types
from typing import List

router = APIRouter()

@router.post("/addLeaveConfig", response_model=AdminLeaveConfigDataType)
async def add_leave_config(
    admin_id: int = Body(embed=True),
    session_id: int = Body(embed=True),
    student_leaves: List[StudentLeaveType]=Body(embed=True, default=[]),
    staff_leaves: List[StaffLeaveType]=Body(embed=True, default=[]),
    token_data: union_of_all_permission_types = Depends(can_change_leave_config)
):
    admin_leave_config = await AdminLeaveConfigTable.create(
        admin_id=admin_id,
        session_id=session_id,
        staff_leaves=staff_leaves,
        student_leaves=student_leaves,
        updated_by_id=token_data.user_id
    )
    return admin_leave_config.dict()

@router.put("/changeLeaveConfig", response_model=AdminLeaveConfigDataType)
async def change_leave_config(
    admin_id: int=Body(embed=True),
    sesson_id: int = Body(embed=True),
    student_leaves: List[StudentLeaveType]=Body(embed=True, default=[]),
    staff_leaves: List[StaffLeaveType]=Body(embed=True, default=[]),
    token_data: union_of_all_permission_types = Depends(can_change_leave_config)
):
    admin_leave_conf = await AdminLeaveConfigTable.update(
        query_params={
            "admin_id": admin_id,
            "session_id": sesson_id,
            "active":True
        },
        **{
            "student_leaves":[l.dict() for l in student_leaves],
            "staff_leaves": [l.dict() for l in staff_leaves],
            "updated_by_id": token_data.user_id
        }
    )
    return admin_leave_conf.dict()

@router.get("/getLeaveConfig", response_model=AdminLeaveConfigDataType)
async def get_leave_config(
    admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types=Depends(can_view_leave_config)
):
    admin_leave_config = await AdminLeaveConfigTable.get(
        admin_id=admin_id,
        session_id=session_id,
        updated_by_id=token_data.user_id
    )
    return admin_leave_config.dict()