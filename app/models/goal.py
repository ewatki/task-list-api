from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal", lazy='select')

    # @classmethod
    # # in class methods, cls must come first. it's a reference to the class itself
    # def from_dict(cls, task_data):
    #     new_goal = goal(
    #         title=goal_data["title"]
    #     )

    #     return new_goal