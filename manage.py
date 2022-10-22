import sys, subprocess, time
from colorama import Fore
from tortoise import run_async, Tortoise
from db_management.models import RolesEnum
from project.config import DBURL
from tortoise.transactions import in_transaction, atomic
from db_management.models import Trigger, UserDB, AppStaff, Designation
from project.sql.sql_queries import auto_handle_created_at, auto_handle_updated_at, auto_now_add_trigger, auto_now_trigger
import uvicorn
from project.config import DEPLOYMENT_DETAILS
from tortoise.models import Model
from project.main import db_config
from auth.auth_config import pwd_context

class Tables:
    def __init__(self):
        self.created_at_table_names = []
        self.updated_at_table_names = []

    def get_all_table_names_with_created_at_or_updated_at_columns(self):
        for cls in Model.__subclasses__():
            cls_name = cls.__name__
            if "created_at" in cls._meta.fields:
                self.created_at_table_names.append(cls_name.casefold())
            if "updated_at" in cls._meta.fields:
                self.updated_at_table_names.append(cls_name.casefold())

async def create_trigger_functions():
    await Tortoise.init(
        db_url=DBURL,
        modules = {"models": db_config["apps"]["models"]["models"]}
    )
    async with in_transaction("default") as conn:
        await conn.execute_script(auto_handle_created_at)
    await Trigger.create(name = "auto_handle_created_at")
    
    async with in_transaction("default") as conn:
        await conn.execute_script(auto_handle_updated_at)
    await Trigger.create(name = "auto_handle_updated_at")
    

async def execute_triggers():
    await Tortoise.init(
        db_url=DBURL,
        modules = {"models": db_config["apps"]["models"]["models"]}
    )

    created_at_trigger_details = await Trigger.filter(name = "auto_handle_created_at")
    if len(created_at_trigger_details) == 0:
        async with in_transaction("default") as conn:
            await conn.execute_script(auto_handle_created_at)
        await Trigger.create(name = "auto_handle_created_at")
        created_at_trigger_details = await Trigger.filter(name = "auto_handle_created_at")

    tables = Tables()
    tables.get_all_table_names_with_created_at_or_updated_at_columns()

    not_triggered_created_at_tables = []
    for table in tables.created_at_table_names:
        if created_at_trigger_details[0].trigger_details.get(table) is None or not created_at_trigger_details[0].trigger_details.get(table):
            not_triggered_created_at_tables.append(table)
    
    updated_at_trigger_details = await Trigger.filter(name = "auto_handle_updated_at")
    if len(updated_at_trigger_details) == 0:
        async with in_transaction("default") as conn:
            await conn.execute_script(auto_handle_updated_at)
        await Trigger.create(name = "auto_handle_updated_at")
        updated_at_trigger_details = await Trigger.filter(name = "auto_handle_updated_at")
        
    not_triggered_updated_at_tables = []
    for table in tables.updated_at_table_names:
        if updated_at_trigger_details[0].trigger_details.get(table) is None or not updated_at_trigger_details[0].trigger_details.get(table):
            not_triggered_updated_at_tables.append(table)
    
    created_at_trigger_json = created_at_trigger_details[0].trigger_details
    for table in not_triggered_created_at_tables:
        async with in_transaction("default") as conn:
            await conn.execute_script(auto_now_add_trigger(table))
        created_at_trigger_json[table] = True
    await created_at_trigger_details[0].update_from_dict({"trigger_details": created_at_trigger_json}).save()
    
    updated_at_trigger_json = updated_at_trigger_details[0].trigger_details
    for table in not_triggered_updated_at_tables:
        async with in_transaction("default") as conn:
            await conn.execute_script(auto_now_trigger(table))
        updated_at_trigger_json[table] = True
    await updated_at_trigger_details[0].update_from_dict({"trigger_details": updated_at_trigger_json}).save()
 
async def create_superuser(
        username, password, name, phone_number, address_line1, address_line2, city, add_code, email, designation
    ):
    await Tortoise.init(
        db_url=DBURL,
        modules = {"models": db_config["apps"]["models"]["models"]}
    )
    @atomic()
    async def save_data(
        username, password, name, phone_number, address_line1, address_line2, city, add_code, email, designation
    ):
        permissions_json = {}
        hashed_pwd = pwd_context.hash(password)
        user = await UserDB.create(username=username, password=hashed_pwd)
        
        appstaff = await AppStaff.create(
            user = user,
            name = name,
            phone_number = phone_number,
            email = email,
            address_line1 = address_line1,
            address_line2 = address_line2,
            address_code = add_code,
            address_city = city
        )
        
        await Designation.create(user=user, role="appstaff", designation=designation, permissions_json=permissions_json, role_instance_id=appstaff.id)
    await save_data(username, password, name, phone_number, address_line1, address_line2, city, add_code, email, designation)

def check_null(field, value):
    if value is not None and value.strip()!="":
        return value
    value = input(f"{field} can not be empty.")
    return check_null(field, value)

if __name__ == "__main__":
    if sys.argv == ["manage.py", "init-db"]:
        subprocess.run(["aerich", "init", "-t", "project.main.db_config"])
        subprocess.run(["aerich", "init-db"])
        print(Fore.YELLOW, "Creating triggers.")
        run_async(execute_triggers())
        print(Fore.GREEN, "Triggers Created.")
        print(Fore.WHITE, ".......................")
    
    if sys.argv == ["manage.py", "migrate"]:
        print(Fore.LIGHTRED_EX, "Please give this migration a name")
        migration_name = input()
        commands = [["aerich", "migrate", "--name", migration_name], ["aerich", "upgrade"]]
        for cmd in commands:
            subprocess.run(cmd)
        print(Fore.YELLOW, "Creating triggers.")
        run_async(execute_triggers())
        print(Fore.GREEN, "Triggers Created.")
        print(Fore.WHITE, ".......................")
        
    if sys.argv == ["manage.py", "createtriggers"]:
        run_async(execute_triggers())
        
    if sys.argv == ["manage.py", "runserver"]:
        uvicorn.run("project.main:app", port = DEPLOYMENT_DETAILS["PORT"], host=DEPLOYMENT_DETAILS["HOST"], reload=True, debug=True, lifespan="on")

    if sys.argv == ["manage.py", "createsuperuser"]:
        print(Fore.GREEN, "input username")
        username = input()
        print(Fore.BLUE, "input password")
        valid_pwd = False
        while not valid_pwd:
            password= input()
            if len(password)<8:
                print(Fore.RED, "password must contain at least 8 letters and must be alphanumeric.")
            else:
                valid_pwd=True
        print(Fore.GREEN, "input name")
        name = input()
        check_null("name", name)
        print(Fore.BLUE, "input phone_number")
        phone_number = input()
        check_null("phone number", phone_number)
        print(Fore.GREEN, "input email")
        email = input()
        check_null("email", email)
        print(Fore.BLUE, "input address_line1")
        address_line1 = input()
        check_null("address_line1", address_line1)
        print(Fore.GREEN, "input address_line2")
        address_line2 = input()
        print(Fore.BLUE, "input city")
        city = input()
        check_null("city", city)
        print(Fore.GREEN)
        address_code = input("Input Address Code")
        check_null("address_code", address_code)
        designation="App Admin"
        run_async(create_superuser(
            name=name,
            phone_number=phone_number,
            email=email,
            password=password,
            username=username,
            add_code=address_code,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            designation=designation
        ))
        print(Fore.WHITE, "Created SuperUser......")