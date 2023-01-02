from fastapi import Depends, APIRouter, Body
from auth.token_creation_logic import TokenCreationManager
from .auth_config import pwd_context, fresh_token_expires
from .auth_datatypes import UserCreateDataTypeIn, UserLoginIN, UserWithRoleDataType
from db_management.models import UserDB, RolesEnum
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from .auth_logic import UserTable
from typing import List
from project.shared.common_datatypes import SuccessReponse

router = APIRouter()


@router.post('/login')
async def login(userData: UserLoginIN, Authorize: AuthJWT = Depends()):
    '''
    User who are not active or are blocked or her designation and roles are not active, has not been handled very well yet.
    '''

    return await TokenCreationManager.validate_and_create_tokens(userData, Authorize)


@router.get("/refreshToken")
async def refresh_access_token(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    subject = Authorize.get_jwt_subject()
    user_claims = Authorize.get_raw_jwt()
    access_token = Authorize.create_access_token(
        subject=subject, user_claims={"user_claims": user_claims["user_claims"]})
    return {"access_token": access_token}


@router.get("/getFreshAccessToken")
async def get_fresh_access_token_for_special_tasks(password: str, Authorization: AuthJWT = Depends()):
    Authorization.jwt_refresh_token_required()
    subject = Authorization.get_jwt_subject()
    user_claims = Authorization.get_raw_jwt()
    user_id = user_claims["user_claims"]["user_id"]
    users = await UserDB.filter(user_id=user_id).values()
    if len(users) != 1 or not pwd_context.verify(password, users[0]["password"]):
        raise HTTPException(
            status_code=401, detail="Either User Name or Password is wrong.")
    fresh_token = Authorization.create_access_token(subject=subject, user_claims={
                                                    "user_claims": user_claims["user_claims"]}, expires_time=fresh_token_expires, fresh=True)
    return {"fresh_token": fresh_token}


@router.delete("/logout")
async def logout_this_device(Authorization: AuthJWT = Depends()):
    '''This does nothing now. Frontend must delete both jwt access and refresh from cookies or local storage.'''
    Authorization.jwt_required()
    return {"success": True}


@router.post("/createUser", deprecated=True)
async def create_user(user_data: UserCreateDataTypeIn):
    '''DO NOT CALL THIS API. AS THESE CREDENTIALS ARE USELESS FOR NOW.'''
    await UserDB.create(username=user_data.username, password=pwd_context.hash(user_data.password_1))
    return {"Success": True}

@router.get("/listUsersWithUsernameAndRole", response_model=List[UserWithRoleDataType])
async def list_users_with_username_and_role(
    phone_number: str,
    role: RolesEnum
):
    return await UserTable.filter_users_with_phone_number_and_role(phone_number, role)

@router.put("/changePassword", response_model=SuccessReponse)
async def change_password_for_user(
    user_id: int = Body(embed=True),
    old_password: str = Body(embed=True),
    new_password: str = Body(embed=True),
    new_password1: str = Body(embed=True)
):
    if new_password!=new_password1:
        raise HTTPException(422, "Passwords must match.")
    if len(new_password)<8:
        raise HTTPException(422, "Password must be at least eight digits long.")
    success = await UserTable.change_password_for_userid(
        user_id=user_id, old_password=old_password, new_password=new_password)
    return {"success": success}