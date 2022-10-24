from enum import Enum

class AppStaffDesignations(str, Enum):
    sales_executive = "Sales Executive"
    app_admin = "App Admin"

class SuperAdminDesignations(str, Enum):
    super_admin = "Super Admin"
    managing_director = "Managing Director"
    chairman_of_the_group = "Chairman of the group of institutions"

class AdminDesignations(str, Enum):
    admin = "Admin"
    institute_manager = "Institute Manager"
    chairman_of_institute = "Chairman of Institute"

class InstituteStaffDesignations(str, Enum):
    teacher = "Teacher"
    assistant_teacher = "Assistant Teacher"
    principal = "Principal"
    vice_principal = "Vice Principal"
    manager = "Manager"
    primary_wing_head = "Head of Primary Wing"
    junior_wing_head = "Head of Junior Wing"
    senior_wing_head = "Head of Senior Wing"
    peon_manager = "Peon Manager"
    peon = "peon"
    other = "other"

class DesignationManager:
    role_designation_map = {
        "appstaff": AppStaffDesignations,
        "superadmin": SuperAdminDesignations,
        "admin": AdminDesignations,
        "institutestaff": InstituteStaffDesignations
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