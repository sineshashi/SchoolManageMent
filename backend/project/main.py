import appstaff.appstaff_management.asm_apis as asm_apis
import auth.auth_apis as auth_apis
import auth.auth_config as authCofig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from tortoise import generate_config
from tortoise.contrib.fastapi import register_tortoise

from project.config import CORS_CONFIG, DBURL, DOCS_ENABLED

from .custom_openapi import custom_openapi
from .shared.redis_cofig import get_from_redis

if DOCS_ENABLED:
    app = FastAPI()
    app.openapi = custom_openapi(
        app,
        response_schema={
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                },
            },
        },
    )
else:
    app = FastAPI(openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["ALLOWED_HOSTS"],
    allow_credentials=CORS_CONFIG["ALLOWED_CREDENTIALS"],
    allow_headers=CORS_CONFIG["ALLOWED_HEADERS"],
    allow_methods=CORS_CONFIG["ALLOWED_METHODS"],
    expose_headers=CORS_CONFIG["EXPOSE_HEADERS"]
)


@AuthJWT.load_config
def get_config():
    return authCofig.JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


'''
This will not let pass through those requests whose token is saved as key and value as True in redis.
'''


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = get_from_redis(key=jti)
    return entry and entry == True


db_config = generate_config(db_url=DBURL, app_modules={"models": [
                            "project.models", "aerich.models", "auth.auth_models"]})

register_tortoise(app=app, config=db_config,
                  generate_schemas=True, add_exception_handlers=True)

app.include_router(
    router=auth_apis.router,
    prefix="/auth",
    tags=["Authetication and Permissions"]
)

app.include_router(
    router=asm_apis.router,
    prefix="/asm",
    tags=["App Staff Management"]
)
