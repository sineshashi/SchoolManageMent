import appstaff.appstaff_management.asm_apis as asm_apis
import auth.auth_apis as auth_apis
import appstaff.onboarding.onboard_apis as onboarding_apis
import institute_staff_management.ism_apis as ism_apis
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

import re
from starlette.routing import Route

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

@AuthJWT.token_in_denylist_loader
def verify_token_if_not_disabled(_decrypted_token):
    #For advanced implementation
    return False


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

db_config = generate_config(db_url=DBURL, app_modules={"models": [
                            "db_management.models", "aerich.models"]})

register_tortoise(app=app, config=db_config,
                  generate_schemas=True, add_exception_handlers=True)

app.include_router(
    router=auth_apis.router,
    prefix="/auth",
    tags=["Authentication and Permissions"]
)

app.include_router(
    router=asm_apis.router,
    prefix="/asm",
    tags=["App Staff Management"]
)

app.include_router(
    router=onboarding_apis.router,
    prefix="/onboarding",
    tags=["Onboarding"]
)

app.include_router(
    router=ism_apis.router,
    prefix="/ism",
    tags = ["Institute Staff Management"]
)

for route in app.router.routes:
    if isinstance(route, Route):
        route.path_regex = re.compile(route.path_regex.pattern, re.IGNORECASE)