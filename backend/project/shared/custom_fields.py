from dateutil import tz
from typing import Any, Optional, Union, Type
from tortoise import Model, fields
import datetime

utc = tz.gettz("utc")

def to_utc_datetime(value: datetime.datetime)->datetime.datetime:
    if value.tzinfo is None:
        return value
    else:
        value = value.astimezone(utc)
        value.replace(tzinfo=None)
        return value #This will save datetime in given indian time zone by default.

class UTCDateTimeField(fields.DatetimeField):    
    class _db_postgres:
        SQL_TYPE = "TIMESTAMP"
        
    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs: Any) -> None:
        super().__init__(auto_now, auto_now_add, **kwargs)
        
    def to_db_value(self, value: Optional[datetime.datetime], instance: "Union[Type[Model], Model]") -> Optional[datetime.datetime]:
        if value is None:
            return super().to_db_value(value, instance)
        else:
            return to_utc_datetime(value=value)
        
    def to_python_value(self, value: Any) -> Optional[datetime.datetime]:
        if value is None:
            return super().to_python_value(value)
        else:
            return to_utc_datetime(value=value)
   