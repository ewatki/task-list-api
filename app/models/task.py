from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)    

    # @classmethod
    # # in class methods, cls must come first. it's a reference to the class itself
    # def from_dict(cls, task_data):
    #     new_task = Task(
    #         title=task_data["title"],
    #         description=task_data["description"],
    #         completed_at=task_data["completed_at"]
    #     )

    #     return new_task