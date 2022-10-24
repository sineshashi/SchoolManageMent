from .models import InstituteStaff, Designation, RolesEnum
from tortoise.transactions import in_transaction

def fetch_all_institute_staffs_with_designation_sql(admin_id:int, active:bool):
    currently_active = "true" if active else "false"
    blocked = "false" if active else "true"
    return f"SELECT isf.id as id,isf.admin_id as admin_id, isf.user_id as user_id, isf.name as name, isf.super_admin_level as super_admin_level, isf.phone_number as phone_number, isf.email as email, d.designation FROM {InstituteStaff.__name__.casefold()} as isf INNER JOIN {Designation.__name__.casefold()} as d ON isf.id = d.role_instance_id AND d.role = '{RolesEnum.institutestaff}' WHERE isf.admin_id = {admin_id} AND isf.active = {currently_active} AND isf.blocked = {blocked} AND d.active = {currently_active}"

async def get_list_of_all_staffs_with_designation(admin_id:int, active:bool=True):
    async with in_transaction() as conn:
        results = await conn.execute_query_dict(fetch_all_institute_staffs_with_designation_sql(admin_id, active))
    return results