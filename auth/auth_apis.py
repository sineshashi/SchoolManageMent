from fastapi import Depends, APIRouter
from .auth_config import pwd_context, fresh_token_expires, authjwt_access_token_expires, authjwt_refresh_token_expires
from .auth_datatypes import UserCreateDataTypeIn, UserLoginIN
from db_management.models import UserDB, Designation
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from project.shared.necessities import getRoleModel

router = APIRouter()

@router.post('/login')
async def login(userData: UserLoginIN, Authorize: AuthJWT = Depends()):
    '''
    User who are not active or are blocked or her designation and roles are not active, has not been handled very well yet.
    '''
    
    Authorize.jwt_optional()
    user_data = userData.dict()
    password = user_data["password"]
    users = await UserDB.filter(username=user_data["username"]).values()

    if len(users) != 1 or not pwd_context.verify(password, users[0]["password"]):
        raise HTTPException(status_code=401, detail="Either User Name or Password is wrong.")

    current_designation = await Designation.filter(user_id = users[0]["user_id"], active=True).values(
        designation = "designation",
        permissions_json = "permissions_json",
        designation_id = "id",
        role = "role",
        role_instance_id = "role_instance_id"
    )
    if len(current_designation) == 0:
        raise HTTPException(204, detail="You do not have any active account.")
    
    access_token = Authorize.create_access_token(
        subject=current_designation[0]["role"],
        expires_time=authjwt_access_token_expires,
        user_claims={
                "user_claims": {
                "user_id": users[0]["user_id"],
                "username": users[0]["username"],
                "role_and_permissions": current_designation[0]
                }
            }
        )
    refresh_token = Authorize.create_refresh_token(
        subject=current_designation[0]["role"],
        expires_time=authjwt_refresh_token_expires,
        user_claims={
                "user_claims": {
                "user_id": users[0]["user_id"],
                "username": users[0]["username"],
                "role_and_permissions": current_designation[0]
                }
            }
        )
    user_personal_data = await getRoleModel(current_designation[0]["role"]).filter(id = current_designation[0]["role_instance_id"], active=True, blocked=False).values()
    if len(user_personal_data) == 0 or not users[0]["active"]:
        raise HTTPException(status_code=204, detail="Your account is not active or has been blocked.")
    
    #Here we can write logic for sending msg or notification to user for new device loggin if this in new device.
    return {"access_token": access_token, "refresh_token": refresh_token, "user_data": user_personal_data[0]}

@router.get("/refreshToken")
async def refresh_access_token(Authorize: AuthJWT=Depends()):
    Authorize.jwt_refresh_token_required()
    subject = Authorize.get_jwt_subject()
    user_claims = Authorize.get_raw_jwt()
    access_token = Authorize.create_access_token(subject=subject, user_claims={"user_claims": user_claims["user_claims"]})
    return {"access_token": access_token}

@router.get("/getFreshAccessToken")
async def get_fresh_access_token_for_special_tasks(password: str, Authorization: AuthJWT=Depends()):
    Authorization.jwt_refresh_token_required()
    subject = Authorization.get_jwt_subject()
    user_claims = Authorization.get_raw_jwt()
    user_id = user_claims["user_claims"]["user_id"]
    users = await UserDB.filter(user_id=user_id).values()
    if len(users) != 1 or not pwd_context.verify(password, users[0]["password"]):
        raise HTTPException(status_code=401, detail="Either User Name or Password is wrong.")
    fresh_token = Authorization.create_access_token(subject=subject, user_claims={"user_claims": user_claims["user_claims"]}, expires_time=fresh_token_expires, fresh=True)
    return {"fresh_token": fresh_token}

@router.delete("/logout")
async def logout_this_device(Authorization:AuthJWT=Depends()):
    '''This does nothing now. Frontend must delete both jwt access and refresh from cookies or local storage.'''
    Authorization.jwt_required()
    return {"success": True}

@router.post("/createUser")
async def create_user(user_data: UserCreateDataTypeIn):
    await UserDB.create(username = user_data.username, password = pwd_context.hash(user_data.password1))
    return {"Success": True}