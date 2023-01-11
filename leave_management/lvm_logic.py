from db_management.db_enums import (LeaveTypeEnum, LeaveStatusEnum, MeetingEnum, ApproverTypeEnum,
                                    StaffLeaveApproverTypeEnum, StudentLeaveApproverTypeEnum)
from fastapi import HTTPException
from typing import List, Optional, Dict
from db_management.models import (AdminLeaveConfig,
                                LeaveDetail, Meeting, StudentLeaveDetail, InstituteStaffLeaveDetail)
import datetime
from .lvm_datatype import (StaffLeaveType, StudentLeaveType, LeaveDataTypeOut, ClassGroupDataTypeForLeave,
                            StaffDataTypeForLeave, SectionDataTypeForLeave, StudentDataTypeForLeave)
from tortoise.transactions import atomic
import pytz
from tortoise.queryset import QuerySet, ValuesQuery


class AdminLeaveConfigTable:
    _model = AdminLeaveConfig

    def __init__(
        self,
        id: int,
        staff_leaves: List[StaffLeaveType] = [],
        student_leaves: List[StudentLeaveType] = [],
        **kwargs
    ):
        self.id = id
        self.staff_leaves = staff_leaves
        self.student_leaves = student_leaves

    def dict(self) -> Dict:
        return {
            "id": self.id,
            "staff_leaves": [leave.dict() for leave in self.staff_leaves],
            "student_leaves": [leave.dict() for leave in self.staff_leaves]
        }

    @classmethod
    async def get(cls: "AdminLeaveConfigTable", **kwargs) -> "AdminLeaveConfigTable":
        config_model_instance = await cls._model.get(**kwargs)
        staff_leaves = config_model_instance.staff_leaves
        student_leaves = config_model_instance.student_leaves
        return cls(
            id=config_model_instance.id,
            staff_leaves=[StaffLeaveType(**leave) for leave in staff_leaves],
            student_leaves=[StudentLeaveType(**leave)
                            for leave in student_leaves]
        )

    @classmethod
    async def create(
        cls: "AdminLeaveConfigTable",
        admin_id: int,
        session_id: int,
        staff_leaves: List[StaffLeaveType] = [],
        student_leaves: List[StudentLeaveType] = [],
        **kwargs
    ) -> "AdminLeaveConfigTable":
        createdobj, _ = await cls._model.update_or_create(
            admin_id=admin_id,
            session_id=session_id,
            defaults={
                "staff_leaves":[leave.dict() for leave in staff_leaves],
                "student_leaves":[leave.dict() for leave in student_leaves],
                **kwargs
            }
        )
        return cls(id=createdobj.id, staff_leaves=staff_leaves, student_leaves=student_leaves)

    @classmethod
    async def update(cls: "AdminLeaveConfigTable", query_params: Dict, **kwargs) -> "AdminLeaveConfigTable":
        await cls._model.filter(**query_params).update(**kwargs)
        return await cls.get(**query_params)


class LeaveTime:
    _model = Meeting

    def __init__(
        self,
        date: datetime.date,
        meeting: MeetingEnum,
        orm_obj:Optional[Meeting]=None,
        id: Optional[int]=None,
        **kwargs
    ):
        self.date = date
        self.meeting = meeting
        self.orm_obj = orm_obj
        self.id = id

    def __eq__(self, o: "LeaveTime") -> bool:
        return (self.date == o.date and self.meeting == o.meeting)

    def __lt__(self, o: "LeaveTime") -> bool:
        return (self.date < o.date or (self.date == o.date and self.meeting < o.meeting))

    def __le__(self, o: "LeaveTime") -> bool:
        return self == o or self < o

    def __sub__(self, o: "LeaveTime") -> float:
        if self < o:
            return 0

        delta = self.date - o.date
        diff_days = delta.days
        if self.meeting == o.meeting:
            diff_days += 0.5
        elif self.meeting == 1 and o.meeting == 0:
            diff_days += 1
        return diff_days

    def dict(self):
        return {"date": self.date, "meeting": self.meeting}
        
    @classmethod
    async def from_orm_instance(
        cls: "LeaveTime",
        obj: "Meeting"
    )->"LeaveTime":
        return cls(**obj.__dict__, orm_obj=obj)

    @classmethod
    async def _create(
        cls: "LeaveTime",
        **kwargs
    )->"LeaveTable":
        return await cls._model.create(**kwargs)

    @classmethod
    async def create(
        cls: "LeaveTime",
        date: datetime.datetime,
        meeting: MeetingEnum
    )->"LeaveTime":
        orm_obj = await cls._create(date=date, meeting=meeting)
        return await cls.from_orm_instance(orm_obj)

    @classmethod
    async def update(
        cls: "LeaveTime",
        id: int,
        **kwargs
    ):
        await cls._model.filter(id=id).update(**kwargs)

    async def save(self)->"LeaveTime":
        if self.id is None:
            return await LeaveTime.create(**self.dict())
        await LeaveTime.update(id=self.id, **self.dict())
        return self


class LeaveTable:
    _model = LeaveDetail

    def __init__(
        self,
        leave_type: LeaveTypeEnum,
        leave_status: LeaveStatusEnum,
        leave_start: LeaveTime,
        leave_end: LeaveTime,
        authorizer: ApproverTypeEnum,
        reacted_by: Optional[ApproverTypeEnum] = None,
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        reacted_at: Optional[datetime.datetime] = None,
        description: Optional[str] = None,
        leave_id: Optional[int]=None,
        orm_obj: Optional[LeaveDetail]=None,
        docurl: Optional[str]=None,
        **kwargs
    ):
        if self.leave_to < self.leave_from:
            raise HTTPException(
                422, "leave_from must be less than or equal leave_to.")
        self.leave_id = leave_id
        self.leave_type = leave_type
        self.leave_status = leave_status
        self.leave_start = leave_start
        self.leave_end = leave_end
        self.reacted_by = reacted_by
        self.reacted_at = reacted_at
        self.created_at = created_at
        self.authorizer = authorizer
        self.updated_at = updated_at
        self.description = description
        self.orm_obj = orm_obj
        self.docurl = docurl

    @property
    def leave_count(self) -> float:
        '''Count of leaves between given dates.'''
        return self.leave_to - self.leave_from

    def dict(self) -> Dict:
        return {
            "leave_type": self.leave_type,
            "leave_status": self.leave_status,
            "leave_start": self.leave_start.dict(),
            "leave_end": self.leave_end.dict(),
            "leave_count": self.leave_count,
            "reacted_by": self.reacted_by,
            "reacted_at": self.reacted_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "description": self.description,
            "authorizer": self.authorizer
        }

    @classmethod
    async def from_orm_instance(
        cls: "LeaveTable",
        obj: "LeaveDetail"
    )->"LeaveTable":
        return cls(
            **obj.__dict__,
            leave_start = await LeaveTime.from_orm_instance(await obj.leave_start),
            leave_end = await LeaveTime.from_orm_instance(await obj.leave_end),
            orm_obj = obj
        )

    @classmethod
    async def _get_model(
        cls: "LeaveTable",
        **kwargs
    )->"LeaveDetail":
        return await cls._model.get(**kwargs).prefetch_related("leave_start", "leave_end")

    @classmethod
    async def get(cls: "LeaveTable", **kwargs) -> "LeaveTable":
        model_instance = await cls._get_model(**kwargs)
        return await cls.from_orm_instance(model_instance)

    @classmethod
    async def _create(cls: "LeaveTable", **kwargs) -> "LeaveDetail":
        return await cls._model.create(**kwargs)

    @classmethod
    async def create(
        cls: "LeaveTable",
        leave_start: LeaveTime,
        leave_end: LeaveTime,
        leave_type: LeaveTypeEnum,
        authorizer: ApproverTypeEnum,
        description: str,
        docurl: str,
        updated_by_id: int
    )->"LeaveTable":
        @atomic()
        async def do():
            leave_start_obj = await leave_start.save()
            leave_end_obj = await leave_end.save()
            obj = await cls._create(
                leave_start=leave_start_obj.orm_obj,
                leave_end = leave_end_obj.orm_obj,
                leave_type=leave_type,
                authorizer=authorizer,
                description=description,
                docurl=docurl,
                updated_by_id=updated_by_id
            )
            return await LeaveTable.from_orm_instance(obj)
        return await do()

    @classmethod
    async def update(
        cls: "LeaveTable",
        query_params : Dict={},
        **kwargs
    )->None:
        await cls._model.filter(**query_params).update(**kwargs)

    @classmethod
    async def update_leave_duration(
        cls: "LeaveTable",
        leave_id: int,
        leave_start: LeaveTime,
        leave_end: LeaveTime,
        updated_by_id: int,
    )->"LeaveTable":
        if leave_start > leave_end:
            raise HTTPException(422, "Leave dates are not ok.")
        @atomic()
        async def do():
            obj = await cls.get(leave_id=leave_id, active=True)
            obj.leave_start.date=leave_start.date
            obj.leave_end.date = leave_end.date
            obj.leave_start.meeting = leave_start.meeting
            obj.leave_end.meeting = leave_end.meeting
            obj.leave_start=await obj.leave_start.save()
            obj.leave_end=await obj.leave_end.save()
            await cls.update(query_params={"leave_id": leave_id}, updated_by_id=updated_by_id)
            return obj
        return await do()

    @classmethod
    async def _filter(
        cls: "LeaveTable",
        **kwargs
    )->QuerySet:
        return await cls._model.filter(**kwargs).prefetch_related("leave_start", "leave_end")

    @classmethod
    async def filter(
        cls: "LeaveTable",
        **kwargs
    )->List["LeaveTable"]:
        return [cls.from_orm_instance(obj) for obj in await cls._filter(**kwargs)]

class StudentLeaveTable:
    _model = StudentLeaveDetail

    def __init__(
        self,
        leave: LeaveTable,
        admin_id: int,
        session_id: int,
        student: Optional[SectionDataTypeForLeave]=None,
        section: Optional[StudentDataTypeForLeave]=None,
        orm_obj: Optional[StudentLeaveDetail]=None,
        **kwargs
    ):
        self.leave = leave
        self.admin_id = admin_id
        self.session_id = session_id
        self.student = student
        self.section = section
        self.orm_obj = orm_obj
        

    def dict(self) -> Dict:
        return {
            "leave": self.leave.dict(),
            "admin_id": self.admin_id,
            "session_id": self.session_id,
            "student": self.student.dict() if self.student is not None else None,
            "section": self.section.dict() if self.section is not None else None
        }
    @classmethod
    async def from_orm_instance(
        cls: "StudentLeaveTable",
        obj: StudentLeaveDetail,
        nested: List[str]=[]
    )->"StudentLeaveTable":
        cntobj = StudentLeaveTable(
            leave=LeaveTable.from_orm_instance(await obj.leave),
            **obj.__dict__,
            orm_obj = obj
        )
        if "student" in nested:
            student_orm_obj = await obj.student
            student = StudentDataTypeForLeave(**student_orm_obj.__dict__)
            cntobj.student = student
        if "section" in nested:
            section_orm_obj = await obj.section
            class_obj = await section_orm_obj.school_class
            section = SectionDataTypeForLeave(
                section_id=section_orm_obj.section_id,
                school_class_id=class_obj.school_class_id,
                class_name=class_obj.class_name,
                section_name=section_orm_obj.section_name
            )
            cntobj.section = section
        return cntobj

    @classmethod
    async def _get(
        cls: "StudentLeaveTable",
        nested: List[str]=[],
        **kwargs
    )->"StudentLeaveDetail":
        '''nested will be used for prefetching given fields.'''
        return await cls._model.get(**kwargs).prefetch_related(*nested, "leave")

    @classmethod
    async def get(
        cls: "StudentLeaveTable",
        nested: List[str]=[],
        **kwargs
    ) -> "StudentLeaveTable":
        obj = await cls._get(nested, **kwargs)
        return await cls.from_orm_instance(obj, nested)

    @classmethod
    async def _create(
        cls: "StudentLeaveTable",
        **kwargs
    )->"StudentLeaveDetail":
        return cls._model.create(**kwargs)

    @classmethod
    async def apply(
        cls: "StudentLeaveTable",
        student_id: int,
        leave_data: LeaveTable,
        updated_by_id: int,
        admin_id: int,
        session_id: int,
        section_id: int
    )->"StudentLeaveTable":
        @atomic()
        async def do():
            leave_obj = await LeaveTable.create(
                leave_start=leave_data.leave_start,
                leave_end=leave_data.leave_end,
                leave_type=leave_data.leave_start,
                authorizer=leave_data.authorizer,
                description=leave_data.description,
                docurl=leave_data.docurl,
                updated_by_id=updated_by_id
            )
            student_leave_obj = await cls._create(
                session_id=session_id,
                admin_id=admin_id,
                student_id=student_id,
                section_id=section_id,
                leave=leave_obj
            )
            return cls.from_orm_instance(obj=student_leave_obj)
        return await do()

    @classmethod
    async def _filter(
        cls: "StudentLeaveTable",
        query_params: Dict = {},
        value_params: Dict = {},
    )->ValuesQuery:
        return await cls._model.filter(**query_params).values(**value_params)

    @classmethod
    async def _from_single_valuesquery(
        cls: "StudentLeaveTable",
        values: Dict,
        nested: List[str]=[]
    )->"StudentLeaveTable":
        leave_start = LeaveTime(values["leave_start_date"], values["leave_start_meeting"])
        leave_end = LeaveTime(values["leave_end_date"], values["leave_end_meeting"])
        leave_obj = LeaveTable(**values, leave_end=leave_end, leave_start=leave_start)

        student_obj=None
        if "student" in nested:
            student_obj = StudentDataTypeForLeave(
                student_id=values["student_id"],
                first_name=values["student_first_name"],
                middle_name=values["student_middle_name"],
                last_name=values["student_last_name"],
                picurl=values["student_picurl"]
            )

        section_obj=None
        if "section" in nested:
            section_obj = SectionDataTypeForLeave(
                section_id=values["section_id"],
                school_class_id=values["school_class_id"],
                class_name=values["class_name"],
                section_name=values["section_name"]
            )
        return StudentLeaveTable(
            leave=leave_obj,
            admin_id=values["admin_id"],
            session_id=values["session_id"],
            student=student_obj,
            section=section_obj
        )

    @classmethod
    async def filter(
        cls: "StudentLeaveTable",
        nested: List[str]=[],
        **kwargs
    )->List[LeaveDataTypeOut]:
        value_params = {
            "admin_id": "admin_id",
            "session_id": "session_id",
            "leave_id": "leave_id",
            "leave_start_date": "leave__leave_start__date",
            "leave_start_meeting": "leave__leave_start__meeting",
            "leave_end_date": "leave__leave_end__date",
            "leave_end_meeting": "leave__leave_end__meeting",
            "leave_type": "leave__leave_type",
            "leave_status": "leave__status",
            "authorizer": "leave__authorizer",
            "reacted_by": "leave__reacted_by",
            "docurl": "leave__docurl",
            "description": "leave__description",
            "created_at": "leave__created_at",
            "updated_at": "leave__updated_at"
        }
        if "student" in nested:
            value_params={
                **value_params,
                "student_id": "student_id",
                "student_first_name": "student__first_name",
                "student_middle_name": "student__middle_name",
                "student_last_name": "student__last_name",
                "student_picurl": "student__picurl"
            }
        if "section" in nested:
            values_params={
                **value_params,
                "section_id": "section_id",
                "class_name": "section__class_name",
                "school_class_id": "section__school_class_id",
                "section_name": "section__section_name"
            }

        values_query = await cls._filter(query_params=kwargs, value_params=values_params)
        return [
            await cls._from_single_valuesquery(vq)
            for vq in values_query
        ]

    @classmethod
    async def react(
        cls: "StudentLeaveTable",
        leave_id: int,
        approver_type: StudentLeaveApproverTypeEnum,
        updated_by_id: int,
        section_id: Optional[int]=None,
        approve: bool=True
    )->"StudentLeaveTable":
        '''Approve or reject the leave.'''
        query_params = {
            "leave_id": leave_id,
            "authorizer": approver_type,
            "leave__active": True,
            "leave__leave_status": LeaveStatusEnum.pending,
        }
        if section_id is not None:
            query_params["section_id"]=section_id

        studentleave = await cls.get(nested=[], **query_params)
        studentleave.leave.leave_status = LeaveStatusEnum.approved if approve else LeaveStatusEnum.rejected
        await LeaveTable.update(
            query_params=query_params,
            **{
                "leave_status": studentleave.leave.leave_status,
                "updated_by_id": updated_by_id,
                "reacted_at": datetime.datetime.now().astimezone(pytz.timezone("UTC"))
            }
        )
        return studentleave

class StaffLeaveTable:
    _model = InstituteStaffLeaveDetail

    def __init__(
        self,
        leave: LeaveTable,
        admin_id: int,
        session_id: int,
        class_group: Optional[ClassGroupDataTypeForLeave]=None,
        staff: Optional[StaffDataTypeForLeave]=None,
        **kwargs
    ):
        self.leave = leave
        self.admin_id = admin_id
        self.session_id = session_id
        self.class_group = class_group,
        self.staff = staff
    
    def dict(self)->Dict:
        return {
            "leave": self.leave.dict(),
            "admin_id": self.admin_id,
            "session_id": self.session_id,
            "class_group": self.class_group.dict() if self.class_group is not None else None,
            "staff": self.staff.dict() if self.staff is not None else None
        }

    @classmethod
    async def from_orm_instance(
        cls: "StaffLeaveTable",
        obj: "InstituteStaffLeaveDetail",
        nested: List[str] = None
    ) -> "StaffLeaveTable":
        leaveobj = await LeaveTable.from_orm_instance(await obj.leave)

        staffobj = None
        if "staff" in nested:
            staff_orm_obj = await obj.staff
            staffobj=StaffDataTypeForLeave(
                staff_id=staff_orm_obj.staff_id,
                name=staff_orm_obj.name,
                pic_url=staff_orm_obj.pic_url
            )
        
        class_group = None
        if "class_group" in nested:
            class_group_orm_obj = await obj.class_group
            class_group = ClassGroupDataTypeForLeave(
                group_id=class_group_orm_obj.group_id,
                group_name=class_group_orm_obj.group_name
            )
        return StaffLeaveTable(
            leave=leaveobj,
            staff=staffobj,
            class_group=class_group,
            **obj.__dict__
        )
    
    @classmethod
    async def _get(
        cls: "StaffLeaveTable",
        nested: List[str]=[],
        **kwargs
    )->InstituteStaffLeaveDetail:
        return await cls._model.get(**kwargs).prefetch_related('leave', **nested)
    
    @classmethod
    async def get(
        cls: "StaffLeaveTable",
        nested: List=[],
        **kwargs
    ):
        ormobj = await cls._get(nested, **kwargs)
        return await cls.from_orm_instance(ormobj, nested)
    
    @classmethod
    async def _create(
        cls: "StaffLeaveTable",
        **kwargs
    )->InstituteStaffLeaveDetail:
        return await cls._model.create(**kwargs)
    
    @classmethod
    async def apply(
        cls: "StaffLeaveTable",
        leave: LeaveTable,
        staff_id: int,
        class_group_id: int,
        admin_id: int,
        session_id: int,
        updated_by_id: int
    ) -> "StaffLeaveTable":
        @atomic()
        async def do():
            leave_obj = await LeaveTable.create(
                leave_start=leave.leave_start,
                leave_end=leave.leave_end,
                leave_type=leave.leave_type,
                authorizer=leave.authorizer,
                description=leave.description,
                docurl=leave.docurl,
                description = leave.description,
                updated_by_id=updated_by_id
            )
            staff_leave_obj = await StaffLeaveTable._create(
                leave=leave_obj,
                session_id=session_id,
                admin_id=admin_id,
                staff_id=staff_id,
                class_group_id=class_group_id
            )
            return await cls.from_orm_instance(staff_leave_obj)
        return await do()

    @classmethod
    async def _filter(
        cls: "StaffLeaveTable",
        query_params: Dict = {},
        value_params: Dict = {},
    )->ValuesQuery:
        return await cls._model.filter(**query_params).values(**value_params)

    @classmethod
    async def _from_single_valuesquery(
        cls: "StaffLeaveTable",
        values: Dict,
        nested: List[str]=[]
    )->"StaffLeaveTable":
        leave_start = LeaveTime(values["leave_start_date"], values["leave_start_meeting"])
        leave_end = LeaveTime(values["leave_end_date"], values["leave_end_meeting"])
        leave_obj = LeaveTable(**values, leave_end=leave_end, leave_start=leave_start)

        staff_obj=None
        if "staff" in nested:
            staff_obj = StaffDataTypeForLeave(
                staff_id=values["staff_id"],
                name=values["name"],
                pic_url=values["pic_url"]
            )

        class_group=None
        if "class_group" in nested:
            class_group = ClassGroupDataTypeForLeave(
                class_group_id=values["group_id"],
                class_group_name=values["group_name"]
            )
        return StaffLeaveTable(
            leave=leave_obj,
            admin_id=values["admin_id"],
            session_id=values["session_id"],
            staff=staff_obj,
            class_group=class_group
        )

    @classmethod
    async def filter(
        cls: "StaffLeaveTable",
        nested: List[str]=[],
        **kwargs
    )->List[LeaveDataTypeOut]:
        value_params = {
            "admin_id": "admin_id",
            "session_id": "session_id",
            "leave_id": "leave_id",
            "leave_start_date": "leave__leave_start__date",
            "leave_start_meeting": "leave__leave_start__meeting",
            "leave_end_date": "leave__leave_end__date",
            "leave_end_meeting": "leave__leave_end__meeting",
            "leave_type": "leave__leave_type",
            "leave_status": "leave__status",
            "authorizer": "leave__authorizer",
            "reacted_by": "leave__reacted_by",
            "docurl": "leave__docurl",
            "description": "leave__description",
            "created_at": "leave__created_at",
            "updated_at": "leave__updated_at"
        }
        if "staff" in nested:
            value_params={
                **value_params,
                "staff_id": "staff_id",
                "name":"staff__name",
                "pic_url": "staff__pic_url"
            }
        if "class_group" in nested:
            values_params={
                **value_params,
                "group_id": "class_group_id",
                "group_name": "class_group__group_name"
            }

        values_query = await cls._filter(query_params=kwargs, value_params=values_params)
        return [
            await cls._from_single_valuesquery(vq)
            for vq in values_query
        ]

    @classmethod
    async def react(
        cls: "StaffLeaveTable",
        leave_id: int,
        approver_type: StaffLeaveApproverTypeEnum,
        updated_by_id: int,
        class_group_id: Optional[int]=None,
        approve: bool=True
    )->"StaffLeaveTable":
        '''Approve or reject the leave.'''
        query_params = {
            "leave_id": leave_id,
            "authorizer": approver_type,
            "leave__active": True,
            "leave__leave_status": LeaveStatusEnum.pending,
        }
        if class_group_id is not None:
            query_params["class_group_id"]=class_group_id

        staffleave = await cls.get(nested=[], **query_params)
        staffleave.leave.leave_status = LeaveStatusEnum.approved if approve else LeaveStatusEnum.rejected
        await LeaveTable.update(
            query_params=query_params,
            **{
                "leave_status": staffleave.leave.leave_status,
                "updated_by_id": updated_by_id,
                "reacted_at": datetime.datetime.now().astimezone(pytz.timezone("UTC"))
            }
        )
        return staffleave
