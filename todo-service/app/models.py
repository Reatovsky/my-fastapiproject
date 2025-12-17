from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class TodoList(Base):
    __tablename__ = "todo_list"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
