from enum import Enum

class AppStaffDesignations(str, Enum):
    sales_executive = "Sales Executive"
    app_admin = "App Admin"

class DesignationManager:
    role_designation_map = {
        "appstaff": AppStaffDesignations
    }
    @staticmethod
    def validate_designation(role:str, designation:str):
        designation_enum = DesignationManager.role_designation_map[role]
        return designation in designation_enum.__dict__

    @staticmethod
    def get_all_designations_for_role(role: str):
        designation_enum = DesignationManager.role_designation_map[role]
        return_values = {}
        for key, member in designation_enum._member_map_.items():
            return_values[key] = member.value
        return return_values