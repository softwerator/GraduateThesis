# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    comments = db.relationship('Comment', backref='user', lazy=True)
    userdetail = db.relationship('UserDetail', backref=db.backref('user', uselist=False))

    def __init__(self):
	    pass

    def save(self, username, email, password):
        self.username = username
        self.email = email
        self.password = Bcrypt().generate_password_hash(password)

    def check(self, username, password):
        user = User.query.filter_by(username = username).first()
        if user is not None:
            if Bcrypt().check_password_hash(user.password, password):
                return user
        return None

    def reset_password(self, password):
        return Bcrypt().generate_password_hash(password)

class UserDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    image = db.Column(db.String)
    description = db.Column(db.Text)
    language = db.Column(db.String(2))
    created_at = db.Column(db.String, nullable=False)
    updated_at = db.Column(db.String)
    last_login_at = db.Column(db.String)
    last_logout_at = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(256), unique=True, nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
