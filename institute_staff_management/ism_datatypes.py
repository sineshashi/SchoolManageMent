from tortoise.contrib.pydantic import pydantic_model_creator
from db_management.designations import DesignationManager
from db_management.models import InstituteStaff, RolesEnum
from pydantic import BaseModel

from permission_management.base_permission import InstituteStaffPermissionReturnType

institute_staff_data_type = pydantic_model_creator(InstituteStaff, exclude_readonly=True)
institute_staff_data_type_out = pydantic_model_creator(InstituteStaff)

class DesignationDataTypeForInstituteStaff(BaseModel):
    designation: DesignationManager.role_designation_map[RolesEnum.institutestaff]
    permissions_json: InstituteStaffPermissionReturnType