from typing import List, Optional

from datetime import date, time
from pydantic import BaseModel
class Taskboard(BaseModel):
    name:str
    owner:str
    users:List[str]

class Task(BaseModel):
    name:str
    description:str
    given_to:str
    status:str
    taskboard_id:str
    deadline:Optional[date] = None
    completion_time: Optional[time] = None

class User(BaseModel):
    name:str
    email:str
    

