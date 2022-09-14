from tortoise.models import Model
from tortoise import fields
from .shared.custom_fields import UTCDateTimeField
import enum

'''All the fields with name created_at will behave as auto_now_add = True automatically and update_at with auto_now = True.
No need to mention those explicitly.'''

class RolesEnum(str, enum.Enum):
    appstaff = "appstaff",
    superadmin = "superadmin",
    admin = "admin"
              
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

class PermissionLevelEnum(str, enum.Enum):
    app_level = "app_level" #These are app level permissions which will be default to every new institue.
    super_admin_level = "super_admin_level" #These permissions will be default to every institution under the admin.
    admin_level = "admin_level" #These will be default to institute level.
    class_level = "class_level" #These wil be default to class level if added.
    section_level = "section_level" #Section level
    individual_level = "individual_level" #Individual level
    
class Permission(Model):
    id = fields.IntField(pk=True)
    role = fields.CharEnumField(RolesEnum,max_length=255, index=True)
    designation = fields.CharField(max_length=255, index=True)
    permissions_json = fields.JSONField(null=False, default = {})
    permission_level = fields.CharEnumField(PermissionLevelEnum, default=PermissionLevelEnum.app_level, max_length=255, index=True)
    permission_level_instance_id = fields.IntField(null=True, index=True) #Id of the instance, e.g. if superadminlevel then superadmin id.
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    created_by = fields.ForeignKeyField("models.UserDB", related_name="created_designations", on_delete=fields.SET_NULL, null=True)
    
class Designation(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name = "designations", on_delete=fields.CASCADE)
    role = fields.CharEnumField(RolesEnum,max_length=255, index=True)    
    role_instance_id = fields.IntField(index=True, null=False)
    designation = fields.CharField(max_length=255, index=True)
    permission = fields.ForeignKeyField("models.Permission", related_name="designations", on_delete=fields.SET_NULL, null=True)
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
    name = fields.CharField(max_length=300)
    phone_number = fields.CharField(max_length=50, null=False, index = True)
    email = fields.CharField(max_length=300, null=False, index = True)
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
    user = fields.ForeignKeyField("models.UserDB", related_name="super_admin", on_delete=fields.CASCADE)
    name = fields.TextField()
    phone_number = fields.CharField(max_length=50, null=False, index = True)
    email = fields.CharField(max_length=300, null=False, index = True)
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
    user = fields.ForeignKeyField("models.UserDB", related_name="admin", on_delete=fields.CASCADE)
    super_admin = fields.ForeignKeyField("models.SuperAdmin", related_name="admin", on_delete=fields.CASCADE)
    name = fields.TextField()
    phone_number = fields.CharField(max_length=50, null=False, index = True)
    email = fields.CharField(max_length=300, null=False, index = True)
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
    