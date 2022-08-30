'''
This file contains some necessary regulations to follow through out the project and must be maintained to avoid bugs \n
and filling incorrect data in database.
'''

from enum import Enum

from ..models import AppStaff

#Maintain below Role Enum and getRoleModelFuntion for each new class extending User model.
class Roles(Enum):
    sdr = "sdr",
    appstaff = "appstaff"
    
def getRoleModel(role: str):
    if role == "appstaff":
        return AppStaff