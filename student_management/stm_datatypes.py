from tortoise.contrib.pydantic import pydantic_model_creator
from db_management.models import Student
from pydantic import BaseModel

StudentDataType = pydantic_model_creator(Student, exclude_readonly=True)