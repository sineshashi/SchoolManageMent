from fastapi import APIRouter, Body, Depends
from permission_management.base_permission import union_of_all_permission_types
from db_management.designations import DesignationManager
from db_management import models

router = APIRouter()

# @router.post("/addNewStudent")