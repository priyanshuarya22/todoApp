from main import db


class Todo(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    time = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    completed = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.String)
    user = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "time": self.time,
            "image": self.image,
            "completed": self.completed,
            "due_date": self.due_date,
            "user": self.user
        }


class UserRole(db.Model):
    user_id = db.Column(db.String, primary_key=True)
    role = db.Column(db.String, nullable=False)
