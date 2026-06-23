from typing import Annotated    
from sqlmodel import SQLModel, Field
from datetime import datetime

class UserBase(SQLModel):
    username: Annotated[str, Field(min_length=1, max_length=50)]
    name: Annotated[str, Field(min_length=1, max_length=50)]
    email: Annotated[str, Field(max_length=100)]

#schema utilizzata nelle post
class UserCreate(UserBase):
    pass

#schema usato nelle get
class UserPublic(UserBase):
    pass

class User(UserBase, table=True):
    username: str = Field(default = None, primary_key=True)
    
