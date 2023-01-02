import datetime
from .auth_config import pwd_context
from db_management.models import UserDB, Designation
from .auth_datatypes import UserWithRoleDataType, CommonProfileData

from db_management.models import (RolesEnum, AppStaff, Admin, SuperAdmin,
                                  InstituteStaff, ParentGaurdian, Student)
import abc
from tortoise import Model
from typing import List, Optional


def create_password_from_dob(dob: datetime.date):
    dobstr = dob.isoformat()
    dobstrs = dobstr.split("-")
    password = ""
    i = -1
    while i >= -len(dobstrs):
        password += dobstrs[i]
        i -= 1

    return password, pwd_context.hash(password)


class AbstractRoleAuthTable(metaclass=abc.ABCMeta):
    _model = Model
    _role = RolesEnum.admin  # SomeRole.

    @abc.abstractclassmethod
    async def filter_data_for_users_login(cls: "AbstractRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        ...


class AppStaffRoleAuthTable(AbstractRoleAuthTable):
    _model = AppStaff
    _role = RolesEnum.appstaff

    @classmethod
    async def filter_data_for_users_login(cls: "AppStaffRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        appstaff = await cls._model.filter(
            id__in=ids, active=True, blocked=False
        )
        users = []
        for profile in appstaff:
            users.append(
                CommonProfileData(
                    role=cls._role,
                    name=profile.name,
                    email=profile.email,
                    picurl=profile.pic_url,
                    id=profile.id
                )
            )
        return users


class SuperAdminRoleAuthTable(AbstractRoleAuthTable):
    _model = SuperAdmin
    _role = RolesEnum.superadmin

    @classmethod
    async def filter_data_for_users_login(cls: "SuperAdminRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        superadmin = await SuperAdmin.filter(id__in=ids, active=True, block=False)
        users = []
        for profile in superadmin:
            users.append(
                CommonProfileData(
                    role=cls._role,
                    name=profile.name,
                    email=profile.email,
                    picurl=profile.pic_url,
                    id=profile.id
                )
            )


class AdminRoleAuthTable(AbstractRoleAuthTable):
    _model = Admin
    _role = RolesEnum.admin

    @classmethod
    async def filter_data_for_users_login(cls: "AdminRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        admins = await cls._model.filter(id__in=ids, active=True, blocked=False)
        users = []
        for profile in admins:
            users.append(
                CommonProfileData(
                    role=cls._role,
                    name=profile.name,
                    email=profile.email,
                    picurl=profile.pic_url,
                    id=profile.id
                )
            )


class InstituteStaffRoleAuthTable(AbstractRoleAuthTable):
    _model = InstituteStaff
    _role = RolesEnum.institutestaff

    @classmethod
    async def filter_data_for_users_login(cls: "InstituteStaffRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        profiles = await cls._model.filter(id__in=ids, active=True, blocked=False)
        users = []
        for profile in profiles:
            users.append(
                CommonProfileData(
                    role=cls._role,
                    name=profile.name,
                    email=profile.email,
                    picurl=profile.pic_url,
                    id=profile.id
                )
            )


class StudentRoleAuthTable(AbstractRoleAuthTable):
    _model = Student
    _role = RolesEnum.student

    @classmethod
    async def filter_data_for_users_login(cls: "StudentRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        profiles = await cls._model.filter(id__in=ids, active=True, blocked=False)
        users = []
        for profile in profiles:
            name = ""
            if profile.first_name is not None:
                name += profile.first_name
            if profile.middle_name is not None:
                name += " "+profile.middle_name
            if profile.last_name is not None:
                name += " "+profile.last_name
            users.append(
                CommonProfileData(
                    role=cls._role,
                    name=name,
                    email=profile.email,
                    picurl=profile.pic_url,
                    id=profile.id
                )
            )


class ParentGaurdianRoleAuthTable(AbstractRoleAuthTable):
    _model = ParentGaurdian
    _role = RolesEnum.parentgaurdian

    @classmethod
    async def filter_data_for_users_login(cls: "ParentGaurdianRoleAuthTable", ids: List[int]) -> List[CommonProfileData]:
        profiles = await cls._model.filter(id__in=ids, active=True, blocked=False)
        users = []
        for profile in profiles:
            name = ""
            if profile.first_name is not None:
                name += profile.first_name
            if profile.middle_name is not None:
                name += " "+profile.middle_name
            if profile.last_name is not None:
                name += " "+profile.last_name
            users.append(
                CommonProfileData(
                    role=cls._role,
                    name=name,
                    email=profile.email,
                    picurl=profile.pic_url,
                    id=profile.id
                )
            )


class RoleMapATableAuthTable:
    roles = {
        RolesEnum.appstaff: AppStaffRoleAuthTable,
        RolesEnum.admin: AdminRoleAuthTable,
        RolesEnum.superadmin: SuperAdminRoleAuthTable,
        RolesEnum.institutestaff: InstituteStaffRoleAuthTable,
        RolesEnum.student: StudentRoleAuthTable,
        RolesEnum.parentgaurdian: ParentGaurdianRoleAuthTable
    }

    @classmethod
    async def fetch_all_existing_profiles_for_given_ids_and_role(
        cls: "RoleMapATableAuthTable", ids: List[int], role: RolesEnum
    ) -> List[CommonProfileData]:
        authtable: "AbstractRoleAuthTable" = cls.roles[role]
        return await authtable.filter_data_for_users_login(ids=ids)


class UserTable:
    def __init__(self, username, hashed_password, user_id: Optional[int] = None):
        self.user_id = user_id
        self.username = username
        self.hashed_password = hashed_password

    @staticmethod
    async def create(phone_number: str, password: str) -> "UserTable":
        hashed_password = pwd_context.hash(password)
        await UserDB.create(username=phone_number, password=hashed_password)
        return UserTable(phone_number, hashed_password)

    @staticmethod
    async def filter_users_with_phone_number_and_role(
        phone_number: str, role: RolesEnum
    ) -> List[UserWithRoleDataType]:
        all_designations = await Designation.filter(
            user__username=phone_number, user__active=True, role=role).prefetch_related("user")

        role_ids = {x.role_instance_id: x.user.user_id for x in all_designations}
        users = await RoleMapATableAuthTable.fetch_all_existing_profiles_for_given_ids_and_role(
            ids=list(role_ids.keys()), role=role
        )

        common_data = []
        for user in users:
            common_data.append(
                UserWithRoleDataType(
                    user_id=role_ids[user.id],
                    phone_number=phone_number,
                    **user.dict()
                )
            )
        return common_data

    @classmethod
    async def get(cls, user_id: int) -> "UserTable":
        user = await UserDB.get(user_id=user_id, active=True)
        return UserTable(user.username, user.password, user_id=user.user_id)

    async def save(self) -> None:
        if self.user_id is None:
            await UserDB.create(username=self.username, password=self.hashed_password)
        else:
            await UserDB.filter(user_id=self.user_id, active=True).update(password=self.hashed_password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @classmethod
    async def change_password_for_userid(cls: "UserTable", user_id: int, old_password: str, new_password: str):
        user = await cls.get(user_id=user_id)
        if user.verify_password(old_password):
            user.hashed_password = pwd_context.hash(new_password)
            await user.save()
            return True
        return False
        