import datetime
from .auth_config import pwd_context

def create_password_from_dob(dob:datetime.date):
    dobstr = dob.isoformat()
    dobstrs = dobstr.split("-")
    password = ""
    i = -1
    while i >= -len(dobstrs):
        password += dobstrs[i]
        i -= 1

    return password, pwd_context.hash(password)