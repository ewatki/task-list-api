from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task
# from app.models.goal import Goal

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def validate_task(task_id): 
    try: 
        task_id = int(task_id)
    except: 
        abort(make_response({"message": f"task {task_id} invalid"}, 400))

    task = Task.query.get(task_id)

    if not task: 
        abort(make_response({"message": f"task {task_id} not found"}, 404))
    
    return task


def validate_task_details():
    pass

# Create a Task: Valid Task with 'null' 'completed at'
@task_bp.route("", methods=["POST"])
def handle_tasks(): 
    # handle the HTTP request body - pasrses JSON body into a Python dict
    request_body = request.get_json()

    # create a new task instance from the request
    if len(request_body) < 2:
        return {"details": "Invalid data"}, 400
    else: 
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"]
        )

    # database collects new changes - adding new_task as a record
    db.session.add(new_task)
    # database saves and commits the new changes
    db.session.commit()

    return {
        "task": 
        {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)
        }
    }, 201

# Get Saved Tasks from the database
@task_bp.route("", methods=["GET"])
def read_all_tasks(): 
    task_response = []

    tasks = Task.query.all()
    if tasks: 
        for task in tasks:
            task_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            })
    return jsonify(task_response)


@task_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id): 
    task = validate_task(task_id)
    return { 
        "task":
        {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }
    }

@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id): 
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return {
        "task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": bool(task.completed_at)
    }}

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id): 
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'})
