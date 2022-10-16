from typing import Dict, Iterable, List, Optional
from .models import AppStaff, Designation, UserDB
from tortoise.transactions import atomic
from .designations import DesignationManager
from tortoise import exceptions

def atomic_transaction(f):
    @atomic()
    async def execute():
        return await f()
    return execute

class _BaseDBInteractionModel:
    def __init__(self):
        self.model = None

    async def get(self, **kwargs):
        return await self.model.get(**kwargs)

    async def filter(self, **kwargs):
        return await self.model.filter(**kwargs)

    async def get_values(self, **kwargs):
        '''
        kwargs for filter params.
        '''
        return await self.model.get(**kwargs).values()

    async def filter_values(self, **kwargs):
        '''
        kwargs for filter params.
        '''
        return await self.model.filter(**kwargs).values()

    async def create(self, **kwargs):
        return await self.model.create(**kwargs)

    async def bulk_create(
        self,
        objects: Iterable,
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
        update_fields: Optional[Iterable[str]] = None,
        on_conflict: Optional[Iterable[str]] = None
    ):
        """
        Bulk insert operation:

        .. note::
            The bulk insert operation will do the minimum to ensure that the object
            created in the DB has all the defaults and generated fields set,
            but may be incomplete reference in Python.

            e.g. ``IntField`` primary keys will not be populated.

        This is recommended only for throw away inserts where you want to ensure optimal
        insert performance.

        .. code-block:: python3

            User.bulk_create([
                User(name="...", email="..."),
                User(name="...", email="...")
            ])

        :param on_conflict: On conflict index name
        :param update_fields: Update fields when conflicts
        :param ignore_conflicts: Ignore conflicts when inserting
        :param objects: List of objects to bulk create
        :param batch_size: How many objects are created in a single query
        """
        return await self.model.bulk_create(objects=objects, batch_size=batch_size, ignore_conflicts=ignore_conflicts, update_fields=update_fields, on_conflict=on_conflict)

    async def update(self, )

class UserTable:
    def __init__(self):
        self.instance = 
    @staticmethod
    async def get(**kwargs)->UserDB:
        instance = await UserDB.get(**kwargs)
        return instance[0]

    @staticmethod
    async def filter(**kwargs)->List[UserDB]:
        return await UserDB.filter(**kwargs)

    @staticmethod
    async def exists(*args, **kwargs)->bool:
        '''
        Send Q parameters as args and simple filters as kwargs.
        '''
        return UserDB.exists(*args, **kwargs)

class AppStaffTable:
    @staticmethod
    async def get(values:bool=False,**kwargs):
        if not values:
            instance = await AppStaff.get(**kwargs)
        else:
            instance = await AppStaff.get(**kwargs).values()
        return instance[0]
        
    @staticmethod
    async def exists(*args, **kwargs)->bool:
        '''
        Send Q parameters as args and simple filters as kwargs.
        '''
        return AppStaff.exists(*args, **kwargs)

    @staticmethod
    async def create(**kwargs):
        return await AppStaff.create(**kwargs)

    @staticmethod
    async def get_or_create(defaults: Optional[Dict] = None, **kwargs):
        return await AppStaff.get_or_create(defaults=defaults, **kwargs)

class DesignationTable:
    @staticmethod
    async def get(values:bool=False,**kwargs):
        if not values:
            instance = await Designation.get(**kwargs)
        else:
            instance = await Designation.get(**kwargs).values()
        return instance[0]
        
    @staticmethod
    async def create(**kwargs):
        role = kwargs.get("role")
        designation = kwargs.get("designation")
        if not DesignationManager.validate_designation(role, designation):
            raise exceptions.ValidationError("Designation is not valid.")
        return await Designation.create(**kwargs)

    @staticmethod
    async def get_or_create(defaults: Optional[Dict] = None, **kwargs):
        return await Designation.get_or_create(defaults=defaults, **kwargs)

    @staticmethod
    async def exists(*args, **kwargs)->bool:
        '''
        Send Q parameters as args and simple filters as kwargs.
        '''
        return Designation.exists(*args, **kwargs)