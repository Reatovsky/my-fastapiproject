from . import models, database
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel


app = FastAPI(title="TODO Service", description="Микросервис по управлению задачами")

@app.on_event("startup")
def up_event():
    database.init_db()


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    
    class Config:
        from_attributes = True


@app.post("/items", response_model=TodoResponse, status_code=201)
def create_todo_item(item: TodoCreate, db: Session = Depends(database.get_db)):
    db_item = models.TodoList(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

@app.get("/items", response_model=List[TodoResponse])
def get_todo_items(db: Session = Depends(database.get_db)):
    return db.query(models.TodoList).all()

@app.get("/items/{item_id}", response_model=TodoResponse)
def get_todo_item(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(models.TodoList).filter(models.TodoList.id == item_id).first()
    
    if item is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return item

@app.put("/items/{item_id}", response_model=TodoResponse)
def update_todo_item(item_id: int, item_update: TodoUpdate, db: Session = Depends(database.get_db)):
    db_item = db.query(models.TodoList).filter(models.TodoList.id == item_id).first()
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

@app.delete("/items/{item_id}", status_code=204)
def delete_todo_item(item_id: int, db: Session = Depends(database.get_db)):
    db_item = db.query(models.TodoList).filter(models.TodoList.id == item_id).first()
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db.delete(db_item)
    db.commit()
    
    return None
