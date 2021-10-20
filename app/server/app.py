from fastapi import FastAPI,HTTPException
from tortoise import models
from .models.models import Todo,Todo_Pydantic,TodoIn_Pydantic,UpdateTodo
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError,register_tortoise
from typing import List,Optional

app = FastAPI()


@app.get("/")
async def read_root():
    return {"ping":"pong"}

class Status(BaseModel):
    message: str

@app.post("/todo",response_model=Todo_Pydantic)
async def create_todo(todo:TodoIn_Pydantic):
    todo_obj = await Todo.create(**todo.dict(exclude_unset=True))
    return await Todo_Pydantic.from_tortoise_orm(todo_obj)

@app.get("/todo",response_model=List[Todo_Pydantic])
async def get_todos():
    return await Todo_Pydantic.from_queryset(Todo.all())

@app.get("/todo/{todo_id}",response_model=Todo_Pydantic)
async def get_todo(todo_id:int):
    return await Todo_Pydantic.from_queryset_single(Todo.get(id=todo_id))

@app.patch("/todo/{todo_id}",response_model=Todo_Pydantic)
async def updated_todo(todo_id:int,todo:UpdateTodo):
    await Todo.filter(id=todo_id).update(**todo.dict(exclude_unset=True))
    return await Todo_Pydantic.from_queryset_single(Todo.get(id=todo_id))

@app.delete("/todo/{todo_id}",response_model=Status)
async def delete_todo(todo_id:int):
    todo = await Todo.filter(id=todo_id).delete()
    if not todo:
        raise HTTPException(status_code=404, detail=f"item {todo_id} not found")
    return Status(message=f"Deleted todo {todo_id}")

register_tortoise(
    app,
    db_url="postgres://postgres:1234@localhost/fastTodo",
    modules={"models":["server.models.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)