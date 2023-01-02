from typing import Union
from auth.auth_datatypes import DesignationDataTypeOutForAuth, UserDataType, UserLoginIN
from permission_management.base_permission import (union_of_all_permission_types, ParentGaurdianPermissionReturnType,
                                                   StudentPermissionJsonType, StudentPermissionReturnType,
                                                   InstituteStaffPermissionJsonType, AdminPermissionReturnDataType,
                                                   AppStaffPermissionReturnDataType, InstituteStaffPermissionReturnType,
                                                   SuperAdminPermissionReturnDataType)
from .auth_config import pwd_context
from db_management.models import (
    Admin, AppStaff, Designation, InstituteStaff, RolesEnum, SuperAdmin, UserDB, Student, ClassSectionSemester,
    StudentSememster, ParentGaurdian)
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
import datetime
from pydantic import BaseModel
from typing import Optional


def verify_password(raw, hashed):
    return pwd_context.verify(raw, hashed)


def convert_datetime_of_vals_to_str(data: Union[dict, BaseModel]):
    if not isinstance(data, dict):
        try:
            data = data.dict()
        except:
            raise HTTPException(500)
    for k, v in data.items():
        if isinstance(v, datetime.datetime) or isinstance(v, datetime.date):
            data[k] = v.isoformat()
    return data


class TokenCreationManager:
    @staticmethod
    async def verify_username_password(password: str, user_id: Optional[int] = None, username: Optional[str] = None) -> UserDataType:
        try:
            query = {}
            if user_id is not None:
                query["user_id"] = user_id
            if username is not None:
                query["username"] = username
            user_data = await UserDB.get(**query, active=True).values()
        except DoesNotExist:
            raise HTTPException(401, "No such user exists")
        except MultipleObjectsReturned:
            raise HTTPException(401, "Username is duplicated by mistake.")
        except Exception:
            raise HTTPException(500, "Some internal error occured.")
        if not verify_password(password, user_data["password"]):
            raise HTTPException(401, "Invalid Password.")
        return UserDataType(**{
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "active": user_data["active"]
        })

    @staticmethod
    async def verify_designation_and_fetch(user_id: int) -> DesignationDataTypeOutForAuth:
        try:
            current_designation = await Designation.get(user_id=user_id, active=True).values(
                designation="designation",
                permissions_json="permissions_json",
                designation_id="id",
                role="role",
                role_instance_id="role_instance_id"
            )
        except DoesNotExist:
            raise HTTPException(406, "No designation assigned for this user.")
        except MultipleObjectsReturned:
            # Either error or return all the desingations. which may be done later in the project.
            raise HTTPException(406, "Many designations found.")
        except:
            raise HTTPException(500, "Some internal error occured.")

        return DesignationDataTypeOutForAuth(**current_designation)

    @staticmethod
    async def get_user_claims_and_permissions_for_appstaff(user_data: UserDataType, designation_data: DesignationDataTypeOutForAuth):
        if designation_data.role != RolesEnum.appstaff:
            raise HTTPException(
                406, f"{designation_data.role} passed instead of appstaff.")
        try:
            app_staff_data = await AppStaff.get(id=designation_data.role_instance_id, active=True, blocked=False)
        except DoesNotExist:
            raise HTTPException(
                401, "This user's appstaff account has been blocked or deactivated.")
        except Exception as e:
            raise e

        user_obtained_from_db = await app_staff_data.user.values(user_id="user_id")
        if user_data.user_id != user_obtained_from_db["user_id"]:
            raise HTTPException(
                406, "Wrong data saved in db. Contact the staff as soon as possible.")

        other_data = {
            "user_data": convert_datetime_of_vals_to_str(user_data),
            "designation_data": convert_datetime_of_vals_to_str(designation_data),
            "user_personal_data": convert_datetime_of_vals_to_str(app_staff_data.__dict__)
        }

        user_claims = AppStaffPermissionReturnDataType(user_id=user_data.user_id, role_instance_id=designation_data.role_instance_id,
                                                       role=designation_data.role, designation=designation_data.designation, designation_id=designation_data.designation_id, other_data=other_data)
        return {
            "user_claims": user_claims
        }

    @staticmethod
    async def get_user_claims_for_super_admin(user_data: UserDataType, designation_data: DesignationDataTypeOutForAuth):
        if designation_data.role != RolesEnum.superadmin:
            raise HTTPException(
                406, f"{designation_data.role} passed instead of appstaff.")
        try:
            super_admin_data = await SuperAdmin.get(id=designation_data.role_instance_id, active=True, blocked=False)
        except DoesNotExist:
            raise HTTPException(
                401, "This user's super admin account has been blocked or deactivated.")
        except Exception:
            raise Exception

        user_obtained_from_db = await super_admin_data.user.values(user_id="user_id")
        if user_data.user_id != user_obtained_from_db["user_id"]:
            raise HTTPException(
                406, "Wrong data saved in db. Contact the staff as soon as possible.")

        admin_ids = await Admin.filter(super_admin_id=super_admin_data.id, active=True).values_list("id", flat=True)
        other_data = {
            "user_data": convert_datetime_of_vals_to_str(user_data),
            "designation_data": convert_datetime_of_vals_to_str(designation_data),
            "user_personal_data": convert_datetime_of_vals_to_str(super_admin_data.__dict__)
        }
        user_claims = SuperAdminPermissionReturnDataType(user_id=user_data.user_id, role_instance_id=designation_data.role_instance_id,
                                                         role=designation_data.role, designation=designation_data.designation, designation_id=designation_data.designation_id, admin_ids=list(admin_ids), other_data=other_data)
        return {
            "user_claims": user_claims
        }

    @staticmethod
    async def get_user_claims_for_admin(user_data: UserDataType, designation_data: DesignationDataTypeOutForAuth):
        if designation_data.role != RolesEnum.admin:
            raise HTTPException(
                406, f"{designation_data.role} passed instead of appstaff.")
        try:
            admin_data = await Admin.get(id=designation_data.role_instance_id, active=True, blocked=False)
        except DoesNotExist:
            raise HTTPException(
                401, "This user's admin account has been blocked or deactivated.")
        except Exception:
            raise Exception

        user_obtained_from_db = await admin_data.user.values(user_id="user_id")
        if user_data.user_id != user_obtained_from_db["user_id"]:
            raise HTTPException(
                406, "Wrong data saved in db. Contact the staff as soon as possible.")

        other_data = {
            "user_data": convert_datetime_of_vals_to_str(user_data),
            "designation_data": convert_datetime_of_vals_to_str(designation_data),
            "user_personal_data": convert_datetime_of_vals_to_str(admin_data.__dict__)
        }
        user_claims = AdminPermissionReturnDataType(user_id=user_data.user_id, role_instance_id=designation_data.role_instance_id, role=designation_data.role,
                                                    designation=designation_data.designation, designation_id=designation_data.designation_id, super_admin_id=admin_data[0].super_admin_id, other_data=other_data)
        return {
            "user_claims": user_claims
        }

    @staticmethod
    async def get_user_claims_for_institute_staff(user_data: UserDataType, designation_data: DesignationDataTypeOutForAuth):
        if designation_data.role != RolesEnum.institutestaff:
            raise HTTPException(
                406, f"{designation_data.role} passed instead of institute_staff")

        try:
            staff_data = await InstituteStaff.get(id=designation_data.role_instance_id, active=True, blocked=False)
        except DoesNotExist:
            raise HTTPException(
                401, "This user's staff account has been blocked or deactivated.")
        except Exception:
            raise Exception

        staff_other_data = await InstituteStaff.get(id=staff_data.id).values(admin_id="admin_id", user_id="user_id", super_admin_id="admin__super_admin_id")
        designation_data.permissions_json = InstituteStaffPermissionJsonType(
            **designation_data.permissions_json)

        if user_data.user_id != staff_other_data["user_id"]:
            raise HTTPException(
                406, "Wrong data saved in db. Contact the staff as soon as possible.")

        other_data = {
            "user_data": convert_datetime_of_vals_to_str(user_data),
            "designation_data": convert_datetime_of_vals_to_str(designation_data),
            "user_personal_data": convert_datetime_of_vals_to_str(staff_data.__dict__)
        }
        user_claims = InstituteStaffPermissionReturnType(
            user_id=user_data.user_id, role_instance_id=designation_data.role_instance_id, role=designation_data.role, designation=designation_data.designation, designation_id=designation_data.designation_id, admin_id=staff_other_data["admin_id"], super_admin_id=staff_other_data["super_admin_id"], permissions_json=designation_data.permissions_json, super_admin_level=staff_data.super_admin_level, other_data=other_data)

        return {
            "user_claims": user_claims
        }

    @staticmethod
    async def get_user_claims_for_student(user_data: UserDataType, designation_data: DesignationDataTypeOutForAuth):
        if designation_data.role != RolesEnum.student:
            raise HTTPException(
                500, "Wrong function called. Cantact to Backend.")

        try:
            student_data = await Student.get(id=designation_data.role_instance_id, user_id=user_data.user_id, active=True, blocked=False)
        except DoesNotExist:
            raise HTTPException(
                401, 'User Data has been deleted or deactivated.')
        except Exception as e:
            raise e

        designation_data.permissions_json = StudentPermissionJsonType(
            **designation_data.permissions_json)
        sections = await StudentSememster.filter(student_id=student_data.id, active=True).values_list('section_id', flat=True)
        class_data = await ClassSectionSemester.filter(section_id__in=list(sections), semester__current=True, active=True).values(
            section_id="section_id",
            admin_id="admin_id"
        )
        if len(class_data) != 1:
            raise HTTPException(
                401, "Data has been saved in many active classes or not in any.")
        section_data = await StudentSememster.get(section_id=class_data[0]["section_id"], student_id=student_data.id).prefetch_related("subjects")
        subject_ids = await section_data.subjects.filter(active=True).values_list("subject_id", flat=True)
        other_data = {
            "user_data": convert_datetime_of_vals_to_str(user_data),
            "designation_data": convert_datetime_of_vals_to_str(designation_data),
            "user_personal_data": convert_datetime_of_vals_to_str(student_data.__dict__)
        }
        user_claims = StudentPermissionReturnType(
            user_id=user_data.user_id, role_instance_id=designation_data.role_instance_id, role=RolesEnum.student,
            designation=designation_data.designation, designation_id=designation_data.designation_id,
            permissions_json=designation_data.permissions_json, admin_id=class_data[
                0]["admin_id"],
            section_id=class_data[0]["section_id"], subject_ids=list(subject_ids), other_data=other_data
        )
        return {"user_claims": user_claims}

    @staticmethod
    async def get_user_claims_for_gaurdian(userdata: UserDataType, desigantiondata: DesignationDataTypeOutForAuth):
        if desigantiondata.role != RolesEnum.parentgaurdian:
            raise HTTPException(
                400, "Wrong function called. Cantact to Backend")

        gaurdian_data = await ParentGaurdian.filter(
            id=desigantiondata.role_instance_id,
            user_id=userdata.user_id, active=True, blocked=False)
        if len(gaurdian_data) == 0:
            raise HTTPException(401, "user's Data has been deleted.")
        other_data = {
            "user_data": convert_datetime_of_vals_to_str(userdata),
            "user_personal_data": convert_datetime_of_vals_to_str(gaurdian_data[0].__dict__),
            "designation_data": convert_datetime_of_vals_to_str(desigantiondata)
        }
        user_claims = ParentGaurdianPermissionReturnType(
            user_id=userdata.user_id, role_instance_id=gaurdian_data[
                0].id, role=RolesEnum.parentgaurdian,
            designation=desigantiondata.designation, designation_id=desigantiondata.designation_id,
            other_data=other_data, permissions_json=desigantiondata.permissions_json
        )
        return {"user_claims": user_claims}

    @staticmethod
    async def get_access_token(auth: AuthJWT, user_claims: union_of_all_permission_types):
        access_token = auth.create_access_token(
            subject=user_claims.role,
            user_claims={"user_claims": user_claims.dict()}
        )
        return access_token

    @staticmethod
    async def get_refresh_token(auth: AuthJWT, user_claims: union_of_all_permission_types):
        refresh_token = auth.create_refresh_token(
            subject=user_claims.role,
            user_claims={"user_claims": user_claims.dict()}
        )
        return refresh_token

    @staticmethod
    async def validate_and_create_tokens(userinput: UserLoginIN, auth: AuthJWT):
        userdata: UserDataType = await TokenCreationManager.verify_username_password(
            user_id=userinput.user_id, password=userinput.password, username=userinput.username)
        designation_data: DesignationDataTypeOutForAuth = await TokenCreationManager.verify_designation_and_fetch(userdata.user_id)

        if designation_data.role == RolesEnum.appstaff:
            user_claims_and_personal_data = await TokenCreationManager.get_user_claims_and_permissions_for_appstaff(userdata, designation_data)
        elif designation_data.role == RolesEnum.superadmin:
            user_claims_and_personal_data = await TokenCreationManager.get_user_claims_for_super_admin(userdata, designation_data)
        elif designation_data.role == RolesEnum.admin:
            user_claims_and_personal_data = await TokenCreationManager.get_user_claims_for_admin(userdata, designation_data)
        elif designation_data.role == RolesEnum.institutestaff:
            user_claims_and_personal_data = await TokenCreationManager.get_user_claims_for_institute_staff(userdata, designation_data)
        elif designation_data.role == RolesEnum.student:
            user_claims_and_personal_data = await TokenCreationManager.get_user_claims_for_student(userdata, designation_data)
        elif designation_data.role == RolesEnum.parentgaurdian:
            user_claims_and_personal_data = await TokenCreationManager.get_user_claims_for_gaurdian(userdata, designation_data)
        else:
            raise HTTPException(401, "Some invalid user type found.")

        access_token = await TokenCreationManager.get_access_token(auth, user_claims_and_personal_data["user_claims"])
        refresh_token = await TokenCreationManager.get_refresh_token(auth, user_claims_and_personal_data["user_claims"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
