from fastapi.exceptions import HTTPException
import typing

class HttpException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: typing.Optional[str] = None,
        headers: typing.Optional[dict] = None,
    ) -> None:
        self.http_exception = HTTPException(status_code, detail, headers)

    def __getattribute__(self, __name: str) -> typing.Any:
        return getattr(self.http_exception, __name)
    
    def __setattr__(self, __name: str, __value: typing.Any) -> None:
        setattr(self.http_exception, __name, __value)