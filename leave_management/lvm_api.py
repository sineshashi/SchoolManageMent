from fastapi import APIRouter, Body, Depends
from typing import List

from permission_management.leave_permission import can_change_leave_config, can_apply_leave_as_student, \
    can_view_leave_config, can_apply_leave_as_staff, can_approve_student_leave, can_update_leave
from .lvm_logic import AdminLeaveConfigTable, StudentLeaveTable,\
    StaffLeaveTable, LeaveTable, LeaveTime
from .lvm_datatype import StudentLeaveType, StaffLeaveType, AdminLeaveConfigDataType, \
    LeaveDetailDataTypeIn, LeaveDataTypeOut, StudentLeaveDataTypeOut, StudentLeaveWithSectionDataTypeOut,\
        StaffLeaveDataTypeOut, LeaveTimeDataType
from permission_management.base_permission import union_of_all_permission_types, is_authenticated, \
    is_app_staff_or_admin_under_super_admin, is_app_staff_or_super_admin
from db_management.db_enums import LeaveStatusEnum, ApproverTypeEnum
from project.shared.common_datatypes import SuccessReponse

router = APIRouter()


@router.post("/addLeaveConfig", response_model=AdminLeaveConfigDataType)
async def add_leave_config(
    admin_id: int = Body(embed=True),
    session_id: int = Body(embed=True),
    student_leaves: List[StudentLeaveType] = Body(embed=True, default=[]),
    staff_leaves: List[StaffLeaveType] = Body(embed=True, default=[]),
    token_data: union_of_all_permission_types = Depends(
        can_change_leave_config)
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
    admin_id: int = Body(embed=True),
    sesson_id: int = Body(embed=True),
    student_leaves: List[StudentLeaveType] = Body(embed=True, default=[]),
    staff_leaves: List[StaffLeaveType] = Body(embed=True, default=[]),
    token_data: union_of_all_permission_types = Depends(
        can_change_leave_config)
):
    admin_leave_conf = await AdminLeaveConfigTable.update(
        query_params={
            "admin_id": admin_id,
            "session_id": sesson_id,
            "active": True
        },
        **{
            "student_leaves": [l.dict() for l in student_leaves],
            "staff_leaves": [l.dict() for l in staff_leaves],
            "updated_by_id": token_data.user_id
        }
    )
    return admin_leave_conf.dict()


@router.get("/getLeaveConfig", response_model=AdminLeaveConfigDataType)
async def get_leave_config(
    admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_leave_config)
):
    admin_leave_config = await AdminLeaveConfigTable.get(
        admin_id=admin_id,
        session_id=session_id,
        updated_by_id=token_data.user_id
    )
    return admin_leave_config.dict()


@router.post("/applyLeaveAsStudent", response_model=LeaveDataTypeOut)
async def apply_leave_as_student(
    leave_data: LeaveDetailDataTypeIn,
    admin_id: int = Body(embed=True),
    session_id: int = Body(embed=True),
    student_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_apply_leave_as_student)
):
    leave_dict = leave_data.dict()
    del leave_dict["leave_start"]
    del leave_dict["leave_end"]
    leave = LeaveTable(
        **leave_dict,
        leave_start=LeaveTime(**leave_data.leave_start.dict()),
        leave_end=LeaveTime(**leave_data.leave_end.dict()))
    student_leave_obj = await StudentLeaveTable.apply(
        student_id, leave, token_data.user_id, admin_id, session_id
    )
    return student_leave_obj.leave.dict()


@router.get("/listAllLeavesAppliedByStudent", response_model=List[LeaveDataTypeOut])
async def list_all_leaves_applied_by_student(
    student_id: int,
    admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types = Depends(is_authenticated)
):
    student_leaves = await StudentLeaveTable.filter(
        nested=[],
        student_id=student_id,
        admin_id=admin_id,
        session_id=session_id
    )
    return [leave.leave.dict() for leave in student_leaves]


@router.get("/listAllStudentLeavesOfSection", response_model=List[StudentLeaveDataTypeOut])
async def list_all_student_leaves_of_section(
    admin_id: int,
    section_id: int,
    token_data: union_of_all_permission_types = Depends(is_authenticated)
):
    student_leaves = await StudentLeaveTable.filter(
        nested=["student"],
        admin_id=admin_id,
        section_id=section_id
    )
    return [leave.dict() for leave in student_leaves]


@router.get("listAllStudentLeavesPendingOfSection", response_model=List[StudentLeaveDataTypeOut])
async def list_all_pending_student_leaves_of_section(
    admin_id: int,
    section_id: int,
    token_data: union_of_all_permission_types = Depends(is_authenticated)
):
    student_leaves = await StudentLeaveTable.filter(
        nested=["student"],
        admin_id=admin_id,
        section_id=section_id,
        leave__leave_status=LeaveStatusEnum.pending
    )
    return [leave.dict() for leave in student_leaves]


@router.get(
    "listAllStudentLeavesAppliedForAdminApproval",
    response_model=List[StudentLeaveWithSectionDataTypeOut]
)
async def list_all_student_leaves_applied_for_admin_approval(
    admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types = Depends(
        is_app_staff_or_admin_under_super_admin)
):
    student_leaves = await StudentLeaveTable.filter(
        nested=["student", "section"],
        admin_id=admin_id,
        session_id=session_id,
        leave__authorizer=ApproverTypeEnum.principal
    )
    return [leave.dict() for leave in student_leaves]


@router.get(
    "/listAllStudentLeavesForSuperAdminApproval",
    response_model=List[StudentLeaveWithSectionDataTypeOut]
)
async def list_all_students_for_super_admin_approval(
    super_admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types = Depends(
        is_app_staff_or_super_admin)
):
    student_leaves = await StudentLeaveTable.filter(
        nested=["student", "section"],
        admin__super_admin_id=super_admin_id,
        session_id=session_id,
        leave__authorizer=ApproverTypeEnum.managing_director
    )
    return [leave.dict() for leave in student_leaves]

@router.post("/approveStudentLeave", response_model=LeaveDataTypeOut)
async def approve_student_leave(
    leave_id: int=Body(embed=True),
    approve_or_reject: bool = Body(embed=True),
    approver_type: ApproverTypeEnum=Body(embed=True),
    section_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_approve_student_leave)
):
    #Not checking the validity of section_id. Assuming that the frontend will send it right.
    #Can be checked if necessary.
    student_leave=await StudentLeaveTable.react(
        leave_id, approver_type, token_data.user_id, section_id, approve_or_reject)

    return student_leave.leave.dict()

@router.post("/applyLeaveAsStaff", response_model=LeaveDataTypeOut)
async def apply_leave_as_staff(
    leave_data: LeaveDetailDataTypeIn,
    admin_id: int = Body(embed=True),
    session_id: int = Body(embed=True),
    staff_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_apply_leave_as_staff)
):
    leave_dict = leave_data.dict()
    del leave_dict["leave_start"]
    del leave_dict["leave_end"]
    leave = LeaveTable(
        **leave_dict,
        leave_start=LeaveTime(**leave_data.leave_start.dict()),
        leave_end=LeaveTime(**leave_data.leave_end.dict()))
    staff_leave_obj = await StaffLeaveTable.apply(
        leave, staff_id, admin_id, session_id, token_data.user_id
    )
    return staff_leave_obj.leave.dict()

@router.get("/listLeavesAppliedByStaff", response_model = List[LeaveDataTypeOut])
async def list_leaves_applied_by_staff(
    staff_id: int,
    admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types=Depends(is_authenticated)
):
    staff_leaves = await StaffLeaveTable.filter(
        staff_id=staff_id, admin_id=admin_id, session_id=session_id)
    return [leave.leave.dict() for leave in staff_leaves]

@router.get("/listStaffLeavesForAdminApproval", response_model=List[StaffLeaveDataTypeOut])
async def list_staff_leaves_for_admin_approval(
    admin_id: int,
    session_id: int,
    token_data: union_of_all_permission_types=Depends(is_app_staff_or_admin_under_super_admin)
):
    staff_leaves = await StaffLeaveTable.filter(
        nested=["staff"], admin_id=admin_id, session_id=session_id, leave__authorizer=ApproverTypeEnum.principal)
    return [leave.dict() for leave in staff_leaves]

@router.post("/ApproveStaffLeave", response_model=List[LeaveDataTypeOut])
async def approve_staff_leave(
    leave_id: int=Body(embed=True),
    approve_or_reject: bool = Body(embed=True),
    approver_type: ApproverTypeEnum=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(is_app_staff_or_admin_under_super_admin)
):
    staff_leave = await StaffLeaveTable.react(
        leave_id=leave_id,
        approver_type=approver_type,
        approve=approve_or_reject,
        updated_by_id=token_data.user_id
    )
    return staff_leave.leave.dict()

@router.put("/updateLeaveDuration", response_model=LeaveDataTypeOut)
async def update_leave(
    start_leave: LeaveTimeDataType,
    end_leave: LeaveTimeDataType,
    admin_id: int=Body(embed=True),
    leave_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_update_leave)
):
    leave = await LeaveTable.update_leave_duration(
        leave_id=leave_id,
        leave_start=LeaveTime(**start_leave.dict()),
        end_leave=LeaveTime(end_leave.dict()),
        updated_by_id=token_data.user_id
    )
    return leave.dict()

@router.put("/changeAuthorizerForLeave", response_model=SuccessReponse)
async def change_leave_authorizer(
    approver: ApproverTypeEnum,
    leave_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_update_leave)
):
    leave = await LeaveTable.update(
        query_params={"leave_id": leave_id, "leave_status": LeaveStatusEnum.pending},
        authorizer=approver,
        updated_by_id=token_data.user_id
    )