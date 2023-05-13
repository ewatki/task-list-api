from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import desc
from datetime import datetime
import requests
import os

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

def validate_model(cls, model_id): 
    try: 
        model_id = int(model_id)
    except: 
        abort(make_response({"message":f"{model_id} invalid type ({type(model_id)})"}, 400))
        # abort(make_response({"message":f"Invalid data"}, 400))
        
    model = cls.query.get(model_id) 

    if not model:
        abort(make_response({"message":f"{cls.__name__.lower()} {model_id} not found"}, 404))

    return model


# Create a Task: Valid Task with 'null' 'completed at'
@task_bp.route("", methods=["POST"])
def handle_tasks(): 
    # handle the HTTP request body - pasrses JSON body into a Python dict
    request_body = request.get_json()

    # create a new task instance from the request
    if len(request_body) < 2:
        return {"details": "Invalid data"}, 400
    else: 
        new_task = Task.from_dict(request_body)

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

    sort_query = request.args.get("sort")

    if sort_query == "asc": 
        tasks = Task.query.order_by(Task.title).all()
    elif sort_query == "desc": 
        tasks = Task.query.order_by(desc(Task.title)).all()
    else: 
        tasks = Task.query.all()

    if tasks: 
        for task in tasks:
            task_response.append(task.to_dict())
    return jsonify(task_response)


@task_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id): 
    task = validate_model(Task, task_id)
    if not task.goal_id: 
        return { 
            "task":
                {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": bool(task.completed_at)
                }
        }
    else: 
        return { 
            "task":
                {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": bool(task.completed_at),
                    "goal_id": task.goal_id
                }
        }



@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id): 
    task = validate_model(Task, task_id)
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
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'})




def handle_slack_api(task_title): 
    url = "https://slack.com/api/chat.postMessage?channel=task-notifications&text=beep%20boop&pretty=1"

    payload = {
        "channel": "C0574HS4KL2", 
        "text": task_title
        }

    auth_key = {"Authorization": f"Bearer {os.environ.get('AUTHORIZATION')}"}

    response = requests.post(url, headers=auth_key, data=payload)

    print(response.text)




@task_bp.route("/<task_id>/<task_status>", methods=["PATCH"])
def update_completed_task(task_id, task_status): 
    task = validate_model(Task, task_id)
    if task: 
        if task_status == "mark_complete":
            task.completed_at = datetime.now()
            # call to API helper fuction here
            handle_slack_api(task.title)
        elif task_status == "mark_incomplete": 
            task.completed_at = None

    db.session.commit()

    return {
        "task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": bool(task.completed_at)
    }}

# Wave 5: Creating a Second Model Goal
# Make a POST request
# Create a Valid Goal
@goal_bp.route("", methods=["POST"])
def handle_goals(): 
    request_body = request.get_json()

    if len(request_body) < 1:
        return {"details": "Invalid data"}, 400
    else: 
        new_goal = Goal(
            title = request_body["title"]
        )

    db.session.add(new_goal)
    db.session.commit()

    return {
        "goal": 
        {
            "id": new_goal.goal_id,
            "title": new_goal.title
        }
    }, 201

@goal_bp.route("", methods=["GET"])
def read_all_goals():
    goal_response = []

    goals = Goal.query.all()

    if goals: 
        for goal in goals:
            goal_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })    
    return jsonify(goal_response), 200

@goal_bp.route("/<goal_id>", methods=["GET"])
def read_goal(goal_id): 
    goal = validate_model(Goal, goal_id)
    return {
        "goal": {
            "id": goal.goal_id,
            "title": goal.title
        }
    }, 200


@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id): 
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.add(goal)
    db.session.commit()

    return {
        "goal": {
            "id": goal.goal_id,
            "title": goal.title
        }}, 200


@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id): 
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return make_response({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'})


@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_tasks_for_goal(goal_id): 
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    for task in request_body["task_ids"]:
        task = validate_model(Task, task)
        goal.tasks.append(task)

    
    db.session.commit()
    return {
        "id": goal.goal_id,
        "task_ids": request_body["task_ids"]
    }



@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def read_tasks_from_goal(goal_id): 
    goal = validate_model(Goal, goal_id)

    goals_tasks = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": []
    }

    for task in goal.tasks: 

        goals_tasks["tasks"].append(task.to_dict())

    return goals_tasks, 200