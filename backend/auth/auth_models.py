from project.shared.custom_fields import UTCDateTimeField
from tortoise.models import Model
from tortoise import fields

class LoginToken(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.UserDB", related_name="user_tokens", on_delete=fields.CASCADE, index=True)
    device_id = fields.CharField(max_length=255, null=True)
    device_name = fields.CharField(null=False, index=True, max_length=500)
    browser_name = fields.CharField(null=False, index=True, max_length=500)
    device_location = fields.CharField(null=True, max_length=50)
    refresh_token = fields.TextField(null=True)
    blocked = fields.BooleanField(default=False, index=True)
    created_at = UTCDateTimeField(null=True)
    updated_at = UTCDateTimeField(null=True)
    
    class Meta:
        unique_together = (("device_name", "browser_name"),)