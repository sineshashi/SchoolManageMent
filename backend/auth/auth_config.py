from pydantic import BaseModel
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
authjwt_access_token_expires: int = datetime.timedelta(seconds=2*60*60)
authjwt_refresh_token_expires: int = datetime.timedelta(seconds=365*60*60)

class JWTSettings(BaseModel):
    authjwt_secret_key: str = "p2s5v8y/A?D(G+KbPeShVmYq3t6w9z$C&E)H@McQfTjWnZr4u7x!A%D*G-JaNdRg"
    authjwt_algorithm: str = "HS512"
    authjwt_access_token_expires: int = authjwt_access_token_expires
    authjwt_refresh_token_expires: int = authjwt_refresh_token_expires
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_token_location = {"headers"}
    
    
fresh_token_expires = datetime.timedelta(seconds=5*60)