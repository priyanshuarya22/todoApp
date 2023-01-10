from ariadne import convert_kwargs_to_snake_case

from api import db
from api.models import Todo


@convert_kwargs_to_snake_case
def resolve_create_todo(obj, info, title, description, time, image, completed, due_date, user):
    try:
        todo = Todo(
            title=title, description=description, time=time, image=image, completed=completed, due_date=due_date,
            user=user
        )
        db.session.add(todo)
        db.session.commit()
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }
    except:
        payload = {
            "success": False,
            "errors": [f"Unexpect error occurred"]
        }

    return payload


@convert_kwargs_to_snake_case
def resolve_mark_done(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        todo.completed = 1
        db.session.add(todo)
        db.session.commit()
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }
    except AttributeError:
        payload = {
            "success": False,
            "error": [f"Todo matching id {todo_id} was not found"]
        }

    return payload


@convert_kwargs_to_snake_case
def resolve_mark_undone(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        todo.completed = 0
        db.session.add(todo)
        db.session.commit()
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }
    except AttributeError:
        payload = {
            "success": False,
            "error": [f"Todo matching id {todo_id} was not found"]
        }

    return payload


@convert_kwargs_to_snake_case
def resolve_delete_todo(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
        payload = {"success": True}

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Todo matching id {todo_id} not found"]
        }

    return payload


@convert_kwargs_to_snake_case
def resolve_update_todo(obj, info, todo_id, title, description, image, due_date):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            todo.title = title
            todo.description = description
            todo.image = image
            todo.due_date = due_date
        db.session.add(todo)
        db.session.commit()
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Todo matching id {todo_id} not found"]
        }

    return payload
