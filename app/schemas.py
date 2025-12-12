from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId

#general way to validate a mongoid
def validate_object_id(value: str) -> str:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid MongoDB ObjectId")
    return value
    
MongoId = Annotated[str, BeforeValidator(validate_object_id)]

class EntryStart(BaseModel):
    name: str = Field(..., example="Work on project")
    project_group_id: MongoId

class EntryUpdate(BaseModel):
    name: Optional[str] = Field(..., example="Work on project")
    project_group_id: Optional[MongoId] =Field(None, example="691cc7113ddac7733853998b")

class Entry(BaseModel):
    id: MongoId
    project_group_id: MongoId
    name: str
    starttime: datetime
    endtime: Optional[datetime] = None
    duration: Optional[int] = None  # time in seconds


#*********************Project managment models*************************
class ProjectCreate(BaseModel):
    name: str = Field(..., example="Serial Link"),
    description: str = Field(..., example="My main project")

class Project(BaseModel):
    id: MongoId
    owner_id: MongoId
    name: str
    description: str
    
class ProjectOfUser(BaseModel):
    owner_id: MongoId
