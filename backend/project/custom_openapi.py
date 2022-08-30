import inspect
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi_jwt_auth import AuthJWT


def custom_openapi(  # noqa: C901, WPS210, WPS231
    app: FastAPI,
    response_schema: Optional[Dict[str, Any]] = None,
) -> Callable[[], Dict[str, Any]]:
    """
    Generate custom openAPI schema.

    This function generates openapi schema based on
    routes from FastAPI application.

    :param app: current FastAPI application.
    :param response_schema: json schema of the response.
    :returns: actual schema generator.
    """

    def openapi_generator() -> Dict[str, Any]:
        # If api schema already exists we do nothing.
        if app.openapi_schema:
            return app.openapi_schema

        # Generate base API schema based on
        # current application properties.
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            license_info=app.license_info,
            contact=app.contact,
            terms_of_service=app.terms_of_service,
            tags=app.openapi_tags,
            servers=app.servers,
            openapi_version=app.openapi_version,
        )

        # Header type from configuration.
        header_type = AuthJWT._header_type  # noqa: WPS437
        scheme_name = f"{header_type} auth"

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        # Add security scheme configuration
        # only if if jwt must be in headers.
        # Because cokies schema doesn't work on
        # swagger page.
        if "headers" in AuthJWT._token_location:  # noqa: WPS437
            openapi_schema["components"]["securitySchemes"] = {
                scheme_name: {
                    "type": "apiKey",
                    "in": "header",
                    "name": AuthJWT._header_name,  # noqa: WPS437
                    "description": (
                        f"Enter: **'{header_type} &lt;JWT&gt;'**, "
                        "where JWT is the access token"
                    ),
                    "bearerFormat": header_type,
                },
            }

        # Get all routes where jwt_optional() or jwt_required
        api_router = [route for route in app.routes if isinstance(route, APIRoute)]

        for route in api_router:
            # Getting python sources of a handler function.
            sources = inspect.getsource(route.endpoint)
            # Handler requires JWT auth if any of these words
            # exist in handler's source code.
            jwt_flags = ["jwt_required", "fresh_jwt_required", "jwt_optional", "jwt_refresh_token_required"]
            for method in route.methods:
                # If handler has jwt_flag inside its source code
                # we add security schema in swagger spec.
                if any([flag in sources for flag in jwt_flags]):
                    method_info = openapi_schema["paths"][route.path][method.lower()]
                    method_info["security"] = [
                        {scheme_name: []},
                    ]
                    method_info["responses"][401] = {  # noqa: WPS432
                        "description": "Authorization failed",
                    }
                    if response_schema is not None:
                        method_info["responses"][401][  # noqa: WPS220, WPS432
                            "content"
                        ] = {
                            "application/json": {"schema": response_schema},
                        }

        # Applying generated openapi schema to our app.
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return openapi_generator