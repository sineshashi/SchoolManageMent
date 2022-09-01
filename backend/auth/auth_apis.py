from typing import Any, List, Optional
from fastapi import Depends, APIRouter
from .auth_config import pwd_context, fresh_token_expires, authjwt_access_token_expires, authjwt_refresh_token_expires
from .auth_datatypes import DeviceIN, UserLoginIN
from project.models import UserDB, Designation
from .auth_models import LoginToken
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from project.shared.memcached_related import memcached_client
from project.shared.necessities import getRoleModel

router = APIRouter()

@router.post('/login')
async def login(userData: UserLoginIN, deviceData: DeviceIN, Authorize: AuthJWT = Depends()):
    '''
    User who are not active or are blocked or her designation and roles are not active, has not been handled very well yet.
    '''
    
    Authorize.jwt_optional()
    user_data = userData.dict()
    password = user_data["password"]
    users = await UserDB.filter(username=user_data["username"]).values()
    if len(users) != 1 or not pwd_context.verify(password, users[0]["password"]):
        raise HTTPException(status_code=401, detail="Either User Name or Password is wrong.")
    
    device_identifier = str(users[0]["user_id"]) + "||" + deviceData.device_model + "||" + deviceData.platform + \
        "||"+deviceData.operating_system+"||"+deviceData.os_version+"||"+deviceData.manufacturer+"||"+deviceData.browser_name
    device_data = deviceData.dict()
    location = device_data.pop("device_location")
    login_token_tuple = await LoginToken.get_or_create(
        device_identifier=device_identifier,
        defaults=device_data
    )
    
    token_instance = login_token_tuple[0]
    
    if token_instance.blocked:
        '''Later we can integrate sms and notification to notify other devices of user.'''
        raise HTTPException(status_code=401, detail="This device has been blocked.")
    
    current_designation = await Designation.filter(user_id = users[0]["user_id"], active=True).values(
        designation = "designation",
        permission = "permission__permissions",
        designation_id = "id",
        role = "role__role",
        role_instance_id = "role__role_instance_id"
    )
    if len(current_designation) == 0:
        raise HTTPException(204, detail="You do not have any active account.")
    
    access_token = Authorize.create_access_token(
        subject=users[0]["role"],
        user_claims={
                "user_claims": {
                "user_id": users[0]["user_id"],
                "username": users[0]["username"],
                "token_id": token_instance.id,
                "role_and_permisions": current_designation[0]
                }
            }
        )
    refresh_token = Authorize.create_refresh_token(
        subject=users[0]["role"],
        user_claims={
                "user_claims": {
                "user_id": users[0]["user_id"],
                "username": users[0]["username"],
                "token_id": token_instance.id,
                "role_and_permissions": current_designation[0]
                }
            }
        )

    if location is not None:
        await LoginToken.filter(id=token_instance.id).update(refresh_token=refresh_token, device_location = location)
    else:
        await LoginToken.filter(id=token_instance.id).update(refresh_token=refresh_token)
    
    cached_data = memcached_client.get(str(users[0]["user_id"]))
    if cached_data is None:
        cached_data = {
            token_instance.id : {
                "token_data": {
                    "access_token": access_token,
                    "blocked": False
                }
            }
        }
    else:
        cached_data[token_instance.id] = {
            "token_data": {
                "access_token": access_token,
                "blocked": False
            }
        }
    
    memcached_client.set(str(users[0]["user_id"]), cached_data) 
    user_personal_data = await getRoleModel(current_designation[0]["role"]).filter(id = current_designation[0]["role_instance_id"], active=True, blocked=False).values()
    if len(user_personal_data) == 0:
        raise HTTPException(status_code=204, detail="Your account is not active or has been blocked.")
    
    #Here we can write logic for sending msg or notification to user for new device loggin if this in new device.
    return {"access_token": access_token, "refresh_token": refresh_token, "user_data": user_personal_data[0]}

@router.get("/refreshToken")
async def refresh_access_token(Authorize: AuthJWT=Depends()):
    Authorize.jwt_refresh_token_required()
    subject = Authorize.get_jwt_subject()
    user_claims = Authorize.get_raw_jwt()
    user_id = user_claims["user_claims"]["user_id"]
    token_id = user_claims["user_claims"]["token_id"]
    cached_data = memcached_client.get(str(user_id))
    if cached_data is None:
        user = await UserDB.filter(user_id=user_id)
        if len(user) == 0:
            raise HTTPException(status_code=204, detail="No data of user found.")
        elif not user[0].active:
            raise HTTPException(status_code=204, detail="This user has been deleted.")
        cached_data = {}
    if token_id not in cached_data:
        token = await LoginToken.filter(id=token_id).values()
        if len(token) == 0:
            raise HTTPException(status_code=401, detail="This is refresh token is not valid for the device.")
        if token[0]["blocked"]:
            raise HTTPException(status_code=401, detail="This device has been blocked.")
        access_token = Authorize.create_access_token(subject=subject, user_claims={"user_claims": user_claims["user_claims"]})
        cached_data[token_id] = {
            "token_data": {
                "access_token": access_token,
                "blocked": False
            }
        }
    else:
        if cached_data[token_id]["token_data"]["blocked"]:
            raise HTTPException(status_code=401, detail="This device has been blocked.")
        access_token = Authorize.create_access_token(subject=subject, user_claims={"user_claims": user_claims["user_claims"]})
        cached_data[token_id]["token_data"]["access_token"] = access_token
    memcached_client.set(str(user_id), cached_data)
    
    return {"access_token": access_token}

@router.get("/allLoggedInDevices")
async def get_all_logged_in_devices(Authorization: AuthJWT=Depends()):
    Authorization.jwt_required()
    user_claims = Authorization.get_raw_jwt()
    user_id = user_claims["user_claims"]["user_id"]
    tokens = await LoginToken.filter(user_id=user_id).values()
    return tokens

@router.get("/getFreshAccessToken")
async def get_fresh_access_token_for_special_tasks(password: str, Authorization: AuthJWT=Depends()):
    Authorization.jwt_refresh_token_required()
    subject = Authorization.get_jwt_subject()
    user_claims = Authorization.get_raw_jwt()
    user_id = user_claims["user_claims"]["user_id"]
    token_id = user_claims["user_claims"]["token_id"]
    cached_data = memcached_client.get(str(user_id))
    users = await UserDB.filter(user_id=user_id).values()
    if len(users) != 1 or not pwd_context.verify(password, users[0]["password"]):
        raise HTTPException(status_code=401, detail="Either User Name or Password is wrong.")
    
    if cached_data is None:
        user = await UserDB.filter(user_id=user_id)
        if len(user) == 0:
            raise HTTPException(status_code=204, detail="No data of user found.")
        elif not user[0].active:
            raise HTTPException(status_code=204, detail="This user has been deleted.")
        cached_data = {}
    if token_id not in cached_data:
        token = await LoginToken.filter(id=token_id).values()
        if len(token) == 0:
            raise HTTPException(status_code=401, detail="This is refresh token is not valid for the device.")
        if token[0]["blocked"]:
            raise HTTPException(status_code=401, detail="This device has been blocked.")
    else:
        if cached_data[token_id]["token_data"]["blocked"]:
            raise HTTPException(status_code=401, detail="This device has been blocked.")
        
    fresh_token = Authorization.create_access_token(subject=subject, user_claims={"user_claims": user_claims["user_claims"]}, expires_time=fresh_token_expires, fresh=True)
    return {"fresh_token": fresh_token}

@router.post("/logoutDevices")
async def logout_devices_and_invalidate_fresh_token(tokenIDs: List[int], block: Optional[bool]=False, Authorization: AuthJWT=Depends()):
    Authorization.fresh_jwt_required()
    user_claims = Authorization.get_raw_jwt()
    user_id = user_claims["user_claims"]["user_id"]
    db_tokens = await LoginToken.filter(id__in = tokenIDs).values(
        token_id = "id",
        refresh_token = "refresh_token"
    )
    if block:
        await LoginToken.filter(id__in=tokenIDs).update(blocked=True)
    cached_tokens = memcached_client.get(str(user_id))
    for db_token in db_tokens:
        if db_token is None:
            continue
        refresh_jti = Authorization.get_jti(db_token["refresh_token"])
        memcached_client.set(refresh_jti, True, expire=authjwt_refresh_token_expires)
    
    updated_cached = cached_tokens
    for token_id, token_data in cached_tokens:
        if token_data["access_token"] is not None:
            access_jti = Authorization.get_jti(token_data["access_token"])
            memcached_client.set(access_jti, True, expire=authjwt_access_token_expires)
            updated_cached[token_id]["token_data"]["access_token"] = None
            if block:
                updated_cached[token_id]["token_data"]["bloked"] = True
    memcached_client.set(str(user_id), updated_cached)
    
    fresh_token = user_claims["jti"]
    memcached_client.set(fresh_token, True, expire=fresh_token_expires)
    return {"success": True}

@router.delete("/logoutThisDevice")
async def logout_this_device(Authorization:AuthJWT=Depends()):
    '''This will expire access token only.'''
    Authorization.jwt_required()
    user_claims = Authorization.get_raw_jwt()
    cached_data = memcached_client.get(str(user_claims["user_claims"]["user_id"]))
    if cached_data.get(user_claims["user_claims"]["token_id"]) is not None:
        cached_data[user_claims["user_claims"]["token_id"]]["token_data"]["access_token"] = None
    memcached_client.set(str(user_claims["user_claims"]["user_id"]), cached_data)
    memcached_client.set(user_claims["jti"], True, expire=authjwt_access_token_expires)
    return {"success": True}