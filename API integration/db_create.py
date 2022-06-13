from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin

csrf = CSRFProtect()


app = Flask(__name__)

app.config['SECRET_KEY'] = 'fiwuebfiwbfiwbefiwbeifbwieufb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_SECRET_KEY'] = 'wpmfpowfpwdfpowmfbwudy'

db = SQLAlchemy(app)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    collections = db.relationship('Collections', backref='User')

class Town(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    collections = db.relationship('Collections', backref='Town')

class Collections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    town_id = db.Column(db.Integer, db.ForeignKey('town.id'), nullable=False)
