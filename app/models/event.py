from typing import Annotated    
from sqlmodel import SQLModel, Field
from datetime import datetime

class EventBase(SQLModel):
    title: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(max_length=500)]
    date: datetime
    location: str

#schema utilizzata nelle post
class EventCreate(EventBase):
    pass

#schema usato nelle get
class EventPublic(EventBase):
    id: int

class Event(EventBase, table=True):
    id: int = Field(default = None, primary_key=True)
    
