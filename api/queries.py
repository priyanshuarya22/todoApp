from .models import Todo
from ariadne import convert_kwargs_to_snake_case


def resolve_todos(obj, info, user):
    try:
        todos = [todo.to_dict() for todo in Todo.query.filter_by(user=user).all()]
        payload = {
            "success": True,
            "todos": todos
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


@convert_kwargs_to_snake_case
def resolve_todo(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }
    except AttributeError:
        payload = {
            "success": False,
            "error": [f"Todo item matching id {todo_id} not found"]
        }

    return payload
