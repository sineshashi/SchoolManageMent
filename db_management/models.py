from tortoise.models import Model
from tortoise import fields

from db_management.db_enums import EducationLevelEnum, EducationStatusEnum
from .custom_fields import UTCDateTimeField
import enum
from db_management.db_validators import validate_email, validate_phone_number

'''All the fields with name created_at will behave as auto_now_add = True automatically and update_at with auto_now = True.
No need to mention those explicitly.'''

class RolesEnum(str, enum.Enum):
    appstaff = "appstaff"
    superadmin = "superadmin"
    admin = "admin"
    institutestaff = "institutestaff"
            
class Trigger(Model):
    trigger_id = fields.IntField(pk = True),
    name = fields.CharField(max_length=100, unique = True, null = False, index = True)
    trigger_details = fields.JSONField(default={})

class UserDB(Model):
    user_id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique = True, null = False, index = True)
    password = fields.CharField(max_length=200, null=False)
    active = fields.BooleanField(default=True, index=True)
    created_at = UTCDateTimeField(null=True, index=True)
    updated_at = UTCDateTimeField(null=True, index = True)
    
    def __str__(self) -> str:
        return self.username

class Designation(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name = "designations", on_delete=fields.CASCADE)
    role = fields.CharEnumField(RolesEnum,max_length=255, index=True)    
    role_instance_id = fields.IntField(index=True, null=False)
    designation = fields.CharField(max_length=255, index=True)
    permissions_json = fields.JSONField(null=False, default = {})
    active = fields.BooleanField(default=True) #Only one instance can be active per user.
    from_time = UTCDateTimeField(null=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)   
    deactivated_at = UTCDateTimeField(null=True) 
    deactivation_reason = fields.TextField(null=True)

class AppStaff(Model):
    # id must be the primary key in every model which is a user like. 
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.UserDB", index=True, null=False, on_delete='CASCADE', related_name="staff")
    name = fields.CharField(max_length=300, index=True)
    phone_number = fields.CharField(max_length=50, null=False, index = True, validators = [validate_phone_number], unique = True)
    email = fields.CharField(max_length=300, null=False, index = True, validators = [validate_email], unique = True)
    account_number = fields.CharField(max_length=250, null=True)
    ifsc_code = fields.CharField(max_length=50, null=True)
    account_holder_name = fields.CharField(max_length=500, null=True)
    address_line1 = fields.TextField()
    address_line2 = fields.TextField(null=True)
    address_city = fields.TextField()
    address_country = fields.TextField(default = "India")
    address_code = fields.TextField()
    active = fields.BooleanField(default=True, index=True, null=False)
    blocked = fields.BooleanField(default=False, index=True, null=False)
    work_from_home = fields.BooleanField(default=True, index=True, null=False)
    pic_url = fields.TextField(null=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    updated_by = fields.ForeignKeyField(model_name="models.UserDB", related_name="updated_staff", on_delete=fields.SET_NULL, null=True)

class SuperAdmin(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name="super_admin", on_delete=fields.CASCADE, index=True)
    name = fields.TextField()
    phone_number = fields.CharField(max_length=50, null=False, index = True, validators = [validate_phone_number], unique = True)
    email = fields.CharField(max_length=300, null=False, index = True, validators = [validate_email], unique=True)
    account_number = fields.CharField(max_length=250, null=True)
    ifsc_code = fields.CharField(max_length=50, null=True)
    account_holder_name = fields.CharField(max_length=500, null=True)
    address_line1 = fields.TextField()
    address_line2 = fields.TextField(null=True)
    address_city = fields.TextField()
    address_country = fields.TextField(default = "India")
    address_code = fields.TextField()
    active = fields.BooleanField(default=True, index=True, null=False)
    blocked = fields.BooleanField(default=False, index=True, null=False)
    pic_url = fields.TextField(null=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    created_by = fields.ForeignKeyField("models.UserDB", related_name="created_super_admins", on_delete=fields.SET_NULL, null=True)
    

class Admin(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name="admin", on_delete=fields.CASCADE, index=True)
    super_admin = fields.ForeignKeyField("models.SuperAdmin", related_name="admin", on_delete=fields.CASCADE)
    name = fields.TextField()
    phone_number = fields.CharField(max_length=50, null=False, index = True, validators = [validate_phone_number], unique = True)
    email = fields.CharField(max_length=300, null=False, index = True, validators = [validate_email], unique=True)
    account_number = fields.CharField(max_length=250, null=True)
    ifsc_code = fields.CharField(max_length=50, null=True)
    account_holder_name = fields.CharField(max_length=500, null=True)
    address_line1 = fields.TextField()
    address_line2 = fields.TextField(null=True)
    address_city = fields.TextField()
    address_country = fields.TextField(default = "India")
    address_code = fields.TextField()
    active = fields.BooleanField(default=True, index=True, null=False)
    blocked = fields.BooleanField(default=False, index=True, null=False)
    pic_url = fields.TextField(null=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    created_by = fields.ForeignKeyField("models.UserDB", related_name="created_admins", on_delete=fields.SET_NULL, null=True)
    
class InstituteStaff(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name="institute_staff", on_delete=fields.CASCADE, index=True)
    admin = fields.ForeignKeyField("models.Admin", related_name="institute_staff", on_delete=fields.CASCADE, index=True)
    super_admin_level = fields.BooleanField(default=False, index=True)
    name = fields.CharField(max_length=500, index=True)
    phone_number = fields.CharField(max_length=20, index=True, validators = [validate_phone_number], unique=True)
    email = fields.CharField(max_length=500, validators = [validate_email], unique=True)
    father_name = fields.CharField(max_length=500)
    mother_name = fields.CharField(max_length=500)
    dob = fields.DateField()
    account_number = fields.CharField(max_length=50, null = True)
    ifsc_code = fields.CharField(max_length=20, null=True)
    account_holder_name = fields.CharField(max_length=500, null=True)
    address_line1 = fields.TextField()
    address_line2 = fields.TextField(null=True)
    address_city = fields.TextField()
    address_country = fields.TextField(default = "India")
    address_code = fields.TextField()
    #Alternate Details
    alternate_phone_number = fields.CharField(max_length=20, validators = [validate_phone_number], null=True, unique = True)
    alternate_email = fields.CharField(max_length=500, null=True, validators = [validate_email], unique = True)
    alternate_address_line1 = fields.TextField(null=True)
    alternate_address_line2 = fields.TextField(null=True)
    alternate_address_city = fields.TextField(null=True)
    alternate_address_country = fields.TextField(default = "India", null=True)
    alternate_address_code = fields.TextField(null=True)
    #Other Details 
    active = fields.BooleanField(default=True, index=True, null=False)
    blocked = fields.BooleanField(default=False, index=True, null=False)
    pic_url = fields.TextField(null=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    created_by = fields.ForeignKeyField("models.UserDB", related_name="created_institute_staffs", on_delete=fields.SET_NULL, null=True)

class EducationDetail(Model):
    id = fields.IntField(pk=True)
    institute_staff = fields.ForeignKeyField("models.InstituteStaff", "education_details", on_delete=fields.CASCADE, index=True)
    level = fields.CharEnumField(EducationLevelEnum, max_length=55, index=True)
    course = fields.TextField(null=False)
    semester_or_year = fields.IntField(default=0) #0 means semester or year not applicable.
    roll_number = fields.IntField(null=True)
    year = fields.IntField(null=False)
    institute_name = fields.TextField(null=False)
    board_or_university = fields.TextField(null=False)
    status = fields.CharEnumField(EducationStatusEnum, max_length=20, null=False)
    subjects = fields.JSONField(null = False, default = [])
    obtained_marks = fields.FloatField(null = True)
    maximum_marks = fields.FloatField(null = True)
    grade = fields.CharField(max_length=20, null = True)
    docurl = fields.TextField(null=True)
    active = fields.BooleanField(default=True, index=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    updated_by = fields.ForeignKeyField("models.UserDB", "updated_education_details", fields.SET_NULL, null=True)
