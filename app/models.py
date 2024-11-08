#app/models.py

#from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db


# Database models:
# Association table for the many-to-many relationship between users and routes
user_route = db.Table('user_route',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('route_id', db.Integer, db.ForeignKey('route.id'), nullable=False),
    db.Column('score', db.Integer, nullable=True),
    db.Column('proposed_grade', db.String(3), nullable=True),
    db.Column('date', db.DateTime, default=datetime.utcnow)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    routes = db.relationship('Route', secondary=user_route, backref='users', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


class Wall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    #location = db.Column(db.String(150), nullable=False)  # ad esempio, città o palestra
    routes = db.relationship('Route', backref='wall', lazy=True)

    def __repr__(self):
        return f"Wall('{self.name}')" #, '{self.location}')"


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(3), nullable=False)
    wall_id = db.Column(db.Integer, db.ForeignKey('wall.id'), nullable=False)
    image_file = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Route('{self.name}', '{self.grade}', '{self.wall.name}')"
    


