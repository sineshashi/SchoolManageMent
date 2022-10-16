from typing import Union
from pydantic import BaseModel
from typing import Union
from db_management.models import RolesEnum, SuperAdmin, Admin
from tortoise.contrib.pydantic import pydantic_model_creator

SuperAdminDataTypeIn = pydantic_model_creator(SuperAdmin, exclude_readonly=True)
AdminDataTypeIn = pydantic_model_creator(Admin, exclude_readonly=True)