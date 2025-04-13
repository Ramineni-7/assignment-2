from typing import List, Optional

from datetime import date, time, datetime
from pydantic import BaseModel, Field


class Workspace(BaseModel):
    title: str
    created_by: str
    users: List[str]
    last_updated: Optional[datetime] = None

class Task(BaseModel):
    title: str
    details: Optional[str] = None
    workspace_id: str
    status: str = Field(..., description="One of: 'pending', 'in_progress', 'completed'")
    assigned_to: List[str] = []
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    unassigned: bool = False
    

class User(BaseModel):
    id: str
    name: str
    email: str
    last_login: Optional[datetime] = None
    

class WorkspaceSummary(BaseModel):
    id: str
    title: str
    created_by: str
    total_mem: int
    users: List[str]
    total_tasks: int = 0
    active_tasks: int = 0
    completed_tasks: int = 0
    last_activity: Optional[datetime] = None


