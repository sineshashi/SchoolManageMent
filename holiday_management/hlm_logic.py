import datetime
from typing import Optional, List, Dict, Type
from db_management.db_enums import DayEnum
from db_management.models import WeeklyHoliday, GeneralHoliday, Admin, ClassSectionSemester
from .hlm_datatypes import (WeeklyHolidayDataTypeIn, AnnualHolidayDataTypeIn, IrregualHolidayDataTypeIn,
                            WeeklyHolidayDataTypeOut, AnnualHolidayDataTypeOut, IrregualHolidayDataTypeOut,
                            AllHolidaysDataTypeOut, AllHolidaysDataTypeOutForSection,
                            IrregualHolidayDataTypeOutForSection)
from tortoise.transactions import atomic
import enum
import abc
from tortoise.models import Model
from pydantic import BaseModel


class AbstractHolidayTable(metaclass=abc.ABCMeta):
    _model: Type[Model]

    @abc.abstractmethod
    def __init__(self):
        ...

    @abc.abstractmethod
    def dict(self) -> Dict:
        ...

    @classmethod
    @abc.abstractmethod
    async def get(cls, **kwargs) -> "AbstractHolidayTable":
        ...

    @classmethod
    @abc.abstractmethod
    async def create(cls, holiday_data: Type[BaseModel]) -> "AbstractHolidayTable":
        ...

    @classmethod
    @abc.abstractmethod
    async def update(cls, holiday_id: int, admin_id: int, **kwargs) -> "AbstractHolidayTable":
        ...

    @classmethod
    @abc.abstractmethod
    async def discard(cls, holiday_id: int, admin_id: int) -> Dict[str, bool]:
        ...


class WeeklyHolidayTable:
    _model = WeeklyHoliday

    def __init__(
        self,
        holiday_id: int,
        day: DayEnum,
        active: bool = True,
        updated_by_id: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        **kwargs
    ):
        self.holiday_id = holiday_id
        self.day = day
        self.active = active
        self.updated_by_id = updated_by_id
        self.created_at = created_at
        self.updated_at = updated_at

    def dict(self) -> Dict:
        return {
            "holiday_id": self.holiday_id,
            "day": self.day,
            "active": self.active,
            "updated_by_id": self.updated_by_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    async def get(
        cls: "WeeklyHolidayTable",
        **kwargs
    ) -> "WeeklyHolidayTable":
        obj = await cls._model.get(**kwargs)
        return cls(**obj.__dict__)

    @classmethod
    async def create(
        cls: "WeeklyHolidayTable",
        holiday_data: WeeklyHolidayDataTypeIn
    ) -> "WeeklyHolidayTable":
        weekly_holiday_model, _ = await cls._model.update_or_create(
            day=holiday_data.day,
            admin_id=holiday_data.admin_id,
            semester_id=holiday_data.semester_id,
            defaults={"updated_by_id": holiday_data.updated_by_id}
        )
        return await cls.get(holiday_id=weekly_holiday_model.holiday_id)

    @classmethod
    async def all(
        cls: "WeeklyHolidayTable",
        admin_id: int,
        semester_id: int
    ) -> "List[WeeklyHolidayTable]":
        '''
        Get all active weekly holidays.
        '''
        weekly_holidays = await cls._model.filter(admin_id=admin_id, semester_id=semester_id, active=True)
        return [cls(**holiday.__dict__) for holiday in weekly_holidays]

    @classmethod
    async def update(
        cls: "WeeklyHolidayTable", holiday_id: int, admin_id: int, **kwargs
    ) -> "WeeklyHolidayTable":
        await cls._model.filter(holiday_id=holiday_id, admin_id=admin_id).update(**kwargs)
        return await cls.get(holiday_id=holiday_id)

    @classmethod
    async def discard(cls: "WeeklyHolidayTable", holiday_id: int, admin_id: int) -> "Dict[str, bool]":
        await cls._model.filter(holiday_id=holiday_id, admin_id=admin_id).update(active=False)
        return {"success": True}


class AnnualHolidayTable:
    _model = GeneralHoliday

    def __init__(
        self,
        holiday_id: int,
        title: str,
        date: datetime.date,
        description: Optional[str] = None,
        picurl: Optional[str] = None,
        active: bool = True,
        updated_by_id: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        **kwargs
    ):
        self.holiday_id = holiday_id
        self.title = title
        self.description = description
        self.date = date
        self.picurl = picurl
        self.active = active
        self.updated_by_id = updated_by_id
        self.created_at = created_at
        self.updated_at = updated_at

    def dict(self) -> Dict:
        return {
            "holiday_id": self.holiday_id,
            "date": self.date,
            "title": self.title,
            "description": self.description,
            "picurl": self.picurl,
            "active": self.active,
            "updated_by_id": self.updated_by_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    async def get(
        cls: "AnnualHolidayTable",
        **kwargs
    ) -> "AnnualHolidayTable":
        obj = await cls._model.get(**kwargs, non_occasion=False)
        return cls(date=obj.start_date, **obj.__dict__)

    @classmethod
    async def create(
        cls: "AnnualHolidayTable",
        holiday_data: AnnualHolidayDataTypeIn
    ) -> "AnnualHolidayTable":
        data = holiday_data.dict()
        del data["date"]
        data["start_date"] = holiday_data.date
        data["end_date"] = holiday_data.date
        data["occasion"] = False
        annual_holiday_model = await cls._model.create(**data)
        return await cls.get(holiday_id=annual_holiday_model.holiday_id)

    @classmethod
    async def all(
        cls: "AnnualHolidayTable",
        admin_id: int,
        semester_id: int
    ) -> "List[AnnualHolidayTable]":
        '''All active annual holidays.'''
        annual_holidays = await cls._model.filter(
            admin_id=admin_id,
            semester_id=semester_id,
            active=True,
            non_occasion=False
        )
        return [cls(date=holiday.start_date, **holiday.__dict__) for holiday in annual_holidays]

    @classmethod
    async def update(
        cls: "AnnualHolidayTable", holiday_id: int, admin_id: int, **kwargs
    ) -> "AnnualHolidayTable":
        if 'date' in kwargs:
            kwargs["start_date"] = kwargs["date"]
            kwargs['end_date'] = kwargs["date"]
            del kwargs["date"]
        if 'non_occasion' in kwargs:
            del kwargs["non_occasion"]
        await cls._model.filter(holiday_id=holiday_id, non_occasion=False, admin_id=admin_id).update(**kwargs)
        return await cls.get(holiday_id=holiday_id)

    @classmethod
    async def discard(cls: "AnnualHolidayTable", holiday_id: int, admin_id: int) -> Dict[str, bool]:
        await cls._model.filter(
            holiday_id=holiday_id, non_occasion=False, admin_id=admin_id
        ).update(active=False)
        return {"success": True}


class SectionTable:
    _model = ClassSectionSemester

    def __init__(
        self,
        section_id: int,
        school_class_id: int,
        class_name: str,
        section_name: Optional[str] = None,
        section_instance: Optional["SectionTable._model"] = None,
        **kwargs
    ):
        self.section_id = section_id
        self.section_name = section_name
        self.school_class_id = school_class_id
        self.class_name = class_name
        self.section_instance = section_instance

    def dict(self) -> Dict:
        return {
            "section_id": self.section_id,
            "school_class_id": self.school_class_id,
            "class_name": self.class_name,
            "section_name": self.section_name
        }

    @classmethod
    async def all_sections_of_an_institute(
        cls: "SectionTable",
        admin_id: int,
        semester_id: int
    ) -> "List[SectionTable]":
        all_sections = await cls._model.filter(
            admin_id=admin_id,
            semester_id=semester_id,
            active=True
        ).prefetch_related("school_class")

        return [
            cls(
                section_id=section.section_id,
                section_name=section.section_name,
                section_instance=section,
                school_class_id=section.school_class.class_id,
                class_name=section.school_class.class_name
            ) for section in all_sections
        ]

    @classmethod
    async def filter_sections_of_an_institute(
        cls: "SectionTable",
        section_ids: List[int] = []
    ) -> "List[SectionTable]":
        all_sections = await cls._model.filter(
            active=True,
            section_id__in=section_ids
        ).prefetch_related("school_class")

        return [
            cls(
                section_id=section.section_id,
                section_name=section.section_name,
                section_instance=section,
                school_class_id=section.school_class.class_id,
                class_name=section.school_class.class_name
            ) for section in all_sections
        ]


class IrregularHolidayTable:
    _model = GeneralHoliday

    def __init__(
        self,
        holiday_id: int,
        title: str,
        start_date: datetime.date,
        end_date: datetime.date,
        description: Optional[str] = None,
        picurl: Optional[str] = None,
        active: bool = True,
        updated_by_id: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        sections: List[SectionTable] = [],
        **kwargs
    ):
        self.title = title
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.picurl = picurl
        self.active = active
        self.updated_by_id = updated_by_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.holiday_id = holiday_id
        self.sections = sections

    def dict(self) -> Dict:
        return {
            "holiday_id": self.holiday_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "title": self.title,
            "description": self.description,
            "picurl": self.picurl,
            "active": self.active,
            "updated_by_id": self.updated_by_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "sections": [section.dict() for section in self.sections]
        }

    @classmethod
    async def get(
        cls: "IrregularHolidayTable",
        **kwargs
    ) -> "IrregularHolidayTable":
        obj = await cls._model.get(**kwargs, non_occasion=True).prefetch_related("sections")
        section_ids = await obj.sections.filter(active=True).values_list("section_id", flat=True)
        sections = await SectionTable.filter_sections_of_an_institute(section_ids=section_ids)
        return cls(**obj.__dict__, sections=sections)

    @classmethod
    async def get_without_sections(
        cls: "IrregularHolidayTable",
        **kwargs
    ) -> "IrregularHolidayTable":
        obj = await cls._model.get(**kwargs, non_occasion=True)
        return cls(**obj.__dict__)

    @classmethod
    async def create(
        cls: "IrregularHolidayTable",
        holiday_data: IrregualHolidayDataTypeIn
    ) -> "IrregularHolidayTable":
        data = holiday_data.dict()
        del data["section_ids"]
        data["non_occasion"] = True

        @atomic()
        async def do():
            section_ids = holiday_data.section_ids
            irregular_data_model = await cls._model.create(**data)
            if section_ids == []:
                sections = await SectionTable.all_sections_of_an_institute(
                    admin_id=holiday_data.admin_id,
                    semester_id=holiday_data.semester_id
                )
            else:
                sections = await SectionTable.filter_sections_of_an_institute(section_ids=section_ids)
            await irregular_data_model.sections.add(*[section.section_instance for section in sections])

            holiday_obj = await cls.get_without_sections(holiday_id=irregular_data_model.holiday_id)
            holiday_obj.sections = sections
            return holiday_obj
        return await do()

    @classmethod
    async def all(
        cls: "IrregularHolidayTable",
        admin_id: int,
        semester_id: int
    ) -> "List[IrregularHolidayTable]":

        irregular_holidays = await cls._model.filter(
            admin=admin_id,
            semester_id=semester_id,
            active=True,
            non_occasion=True).prefetch_related("sections")

        holidays = []
        for holiday in irregular_holidays:
            holidayobj = cls(**holiday.__dict__)
            section_objs = await holiday.sections.filter(active=True).values(
                section_id="section_id",
                section_name="section_name",
                school_class_id="school_class_id",
                class_name="school_class__class_name"
            )
            for section_obj in section_objs:
                section_table = SectionTable(
                    **section_obj
                )
                holidayobj.sections.append(section_table)
            holidays.append(holidayobj)
        return holidays

    @classmethod
    async def update(
        cls: "IrregularHolidayTable", holiday_id: int, admin_id: int, **kwargs
    ) -> "IrregularHolidayTable":
        if 'non_occasion' in kwargs:
            del kwargs["non_occasion"]
        await cls._model.filter(holiday_id=holiday_id, non_occasion=True, admin_id=admin_id).update(**kwargs)
        return await cls.get_without_sections(holiday_id=holiday_id)

    @classmethod
    async def discard(cls: "IrregularHolidayTable", holiday_id: int, admin_id: int) -> Dict[str, bool]:
        await cls._model.filter(
            holiday_id=holiday_id, non_occasion=True, admin_id=admin_id
        ).update(active=False)
        return {"success": True}

    @classmethod
    async def remove_sections(
        cls: "IrregularHolidayTable",
        holiday_id: int,
        section_ids: int
    ) -> "IrregularHolidayTable":
        sections = await SectionTable.filter_sections_of_an_institute(section_ids=section_ids)
        holiday = await cls._model.get(holiday_id=holiday_id, non_occasion=True)
        await holiday.sections.remove(*[section.section_instance for section in sections])
        return await cls.get(holiday_id=holiday_id)

    @classmethod
    async def add_sections(
        cls: "IrregularHolidayTable",
        holiday_id: int,
        section_ids: int
    ) -> "IrregularHolidayTable":
        sections = await SectionTable.filter_sections_of_an_institute(section_ids=section_ids)
        holiday = await cls._model.get(holiday_id=holiday_id, non_occasion=True)
        await holiday.sections.add(*[section.section_instance for section in sections])
        return await cls.get(holiday_id=holiday_id)


class HolidayTypes(str, enum.Enum):
    weekly_holiday_table = "weekly_holiday_table"
    annual_holiday_table = "annual_holiday_table"
    irregular_holiday_table = "irregular_holiday_table"


HolidayTableMap = {
    HolidayTypes.weekly_holiday_table: WeeklyHolidayTable,
    HolidayTypes.annual_holiday_table: AnnualHolidayTable,
    HolidayTypes.irregular_holiday_table: IrregularHolidayTable
}


class AdminHolidayManager:
    _model = Admin

    def __init__(self, admin_id: int, semester_id: int):
        self.admin_id = admin_id
        self.semester_id = semester_id

    async def create_weekly_holiday(
        self, day: DayEnum, updated_by_id: int
    ) -> WeeklyHolidayDataTypeOut:
        holiday_data = WeeklyHolidayDataTypeIn(
            semester_id=self.semester_id,
            admin_id=self.admin_id,
            day=day,
            updated_by_id=updated_by_id
        )
        weekly_holiday = await WeeklyHolidayTable.create(holiday_data=holiday_data)
        return WeeklyHolidayDataTypeOut.parse_obj(weekly_holiday.dict())

    async def create_annual_holiday(
        self,
        title: str,
        date: datetime.date,
        updated_by_id: int,
        description: Optional[str] = None,
        picurl: Optional[str] = None
    ) -> AnnualHolidayDataTypeOut:
        holiday_data = AnnualHolidayDataTypeIn(
            date=date,
            title=title,
            description=description,
            picurl=picurl,
            updated_by_id=updated_by_id,
            admin_id=self.admin_id,
            semester_id=self.semester_id
        )
        annual_holiday = await AnnualHolidayTable.create(holiday_data=holiday_data)
        return AnnualHolidayDataTypeOut.parse_obj(annual_holiday.dict())

    async def create_irregular_holiday(
        self,
        title: str,
        start_date: datetime.date,
        end_date: datetime.date,
        updated_by_id: int,
        description: Optional[str] = None,
        picurl: Optional[str] = None,
        section_ids: List[int] = []
    ) -> IrregualHolidayDataTypeOut:
        holiday_data = IrregualHolidayDataTypeIn(
            start_date=start_date,
            end_date=end_date,
            description=description,
            title=title,
            picurl=picurl,
            admin_id=self.admin_id,
            semester_id=self.semester_id,
            updated_by_id=updated_by_id,
            section_ids=section_ids
        )
        irregular_holiday = await IrregularHolidayTable.create(holiday_data=holiday_data)
        return IrregualHolidayDataTypeOut.parse_obj(irregular_holiday.dict())

    async def fetch_all_holidays(self) -> AllHolidaysDataTypeOut:
        args = [self.admin_id, self.semester_id]
        return AllHolidaysDataTypeOut(
            weekly_holidays=[
                WeeklyHolidayDataTypeOut.parse_obj(holiday.dict())
                for holiday in await WeeklyHolidayTable.all(*args)
            ],
            annual_holidays=[
                AnnualHolidayDataTypeOut.parse_obj(holiday.dict())
                for holiday in await AnnualHolidayTable.all(*args)
            ],
            other_holidays=[
                IrregualHolidayDataTypeOut.parse_obj(holiday.dict())
                for holiday in await IrregularHolidayTable.all(*args)
            ]
        )

    async def get_holiday(
        self, holiday_type: HolidayTypes, holiday_id: int
    ) -> AbstractHolidayTable:
        holiday_table: Type[AbstractHolidayTable] = HolidayTableMap[holiday_type]
        return await holiday_table.get(holiday_id=holiday_id, admin_id=self.admin_id)

    async def update(
        self, holiday_type: HolidayTypes, holiday_id: int, **kwargs
    ) -> AbstractHolidayTable:
        holiday_table: Type[AbstractHolidayTable] = HolidayTableMap[holiday_type]
        return await holiday_table.update(holiday_id=holiday_id, admin_id=self.admin_id, **kwargs)

    async def discard(self, holiday_type: HolidayTypes, holiday_id: int):
        holiday_table: Type[AbstractHolidayTable] = HolidayTableMap[holiday_type]
        return await holiday_table.discard(holiday_id=holiday_id, admin_id=self.admin_id)

    async def add_sections_to_irregular_holiday(
        self,
        holiday_id: int,
        section_ids: List[int]
    ) -> IrregularHolidayTable:
        holiday_table: IrregularHolidayTable = HolidayTableMap[HolidayTypes.irregular_holiday_table]
        return await holiday_table.add_sections(holiday_id=holiday_id, section_ids=section_ids)

    async def remove_sections_from_irregular_holiday(
        self,
        holiday_id: int,
        section_ids: List[int]
    ) -> IrregularHolidayTable:
        holiday_table: IrregularHolidayTable = HolidayTableMap[HolidayTypes.irregular_holiday_table]
        return await holiday_table.remove_sections(holiday_id=holiday_id, section_ids=section_ids)


class SectionHolidayManager:
    _model = ClassSectionSemester

    def __init__(self, admin_id: int, semester_id: int, section_id: int):
        self.admin_id = admin_id
        self.semester_id = semester_id
        self.section_id = section_id

    async def get_irregular_holidays(self) -> List[IrregularHolidayTable]:
        '''Returning objects will have sections attribute empty.'''
        section = await self._model.get(
            section_id=self.section_id,
            admin_id=self.admin_id,
            semester_id=self.semester_id,
            active=True
        ).prefetch_related("holidays")

        holidays = []
        for holiday in await section.holidays.filter(
            active=True,
            non_occasion=True,
            admin_id=self.admin_id,
            semester_id=self.semester_id,
        ):
            holidays.append(IrregularHolidayTable(**holiday.__dict__))
        return holidays

    async def fetch_all_holidays(self) -> AllHolidaysDataTypeOutForSection:
        args = [self.admin_id, self.semester_id]
        return AllHolidaysDataTypeOutForSection(
            weekly_holidays=[
                WeeklyHolidayDataTypeOut.parse_obj(holiday.dict())
                for holiday in await WeeklyHolidayTable.all(*args)
            ],
            annual_holidays=[
                AnnualHolidayDataTypeOut.parse_obj(holiday.dict())
                for holiday in await AnnualHolidayTable.all(*args)
            ],
            other_holidays=[
                IrregualHolidayDataTypeOut.parse_obj(holiday.dict())
                for holiday in await self.get_irregular_holidays()
            ]
        )

    async def get_irregular_holiday(self, holiday_id: int) -> IrregualHolidayDataTypeOutForSection:
        holiday = await IrregularHolidayTable.get_without_sections(holiday_id=holiday_id)
        return IrregualHolidayDataTypeOutForSection.parse_obj(holiday.dict())
