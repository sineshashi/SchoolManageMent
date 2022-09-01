from project.shared.custom_fields import UTCDateTimeField
from tortoise.models import Model
from tortoise import fields

class LoginToken(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name="user_tokens", on_delete=fields.CASCADE, index=True)
    device_model = fields.CharField(null=False, max_length=50, default = "")
    platform = fields.CharField(null=False, max_length=50, default = "")
    operating_system = fields.CharField(null=False, max_length=50, default = "")
    os_version = fields.CharField(null=False, max_length=50, default = "")
    manufacturer = fields.CharField(null=False, max_length=50, default = "")
    browser_name = fields.CharField(null=False, max_length=50, default = "")
    device_identifier = fields.CharField(null=False, max_length=500, index=True)
    device_location = fields.CharField(null=True, max_length=50)
    refresh_token = fields.TextField(null=True)
    blocked = fields.BooleanField(default=False, index=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)