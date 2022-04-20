from flask_login import UserMixin
from datetime import datetime
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    shareholders = db.relationship('Shareholder', backref='User')
    shareforsales = db.relationship('ShareForSale', backref='User')
    shareforpurchase = db.relationship('ShareForPurchase', backref='User')
    activities = db.relationship('Activity', backref='User')

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    current_share_price = db.Column(db.Integer, nullable=False)
    share_total_number = db.Column(db.Integer, nullable=False)
    share_on_hands = db.Column(db.Integer, nullable=False)

    shareholders = db.relationship('Shareholder', backref='Company')
    shareforsales = db.relationship('ShareForSale', backref='Company')
    shareforpurchase = db.relationship('ShareForPurchase', backref='Company')
    activities = db.relationship('Activity', backref='Company')

class Shareholder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    order_share_ammount = db.Column(db.Integer, nullable=False)
    order_share_price = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)

class ShareForSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    ammount_to_sell = db.Column(db.Integer, nullable=False)
    ammount_sold = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class ShareForPurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    ammount_to_buy = db.Column(db.Integer, nullable=False)
    ammount_bought = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operration = db.Column(db.String(20), nullable=False)
    ammount = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)

'''
Just soma data to start with

from project.models import Company, Shareholder, ShareForSale, ShareForPurchase, Activity, db
Apple = Company()
Apple.name = 'Apple'
Apple.current_share_price = 120
Apple.share_total_number = 1200
Apple.share_on_hands = 1100
db.session.add(Apple)

Ibm = Company()
Ibm.name = 'IBM'
Ibm.current_share_price = 110
Ibm.share_total_number = 1100
Ibm.share_on_hands = 1050
db.session.add(Ibm)

Microsoft = Company()
Microsoft.name = 'Microsoft'
Microsoft.current_share_price = 90
Microsoft.share_total_number = 900
Microsoft.share_on_hands = 900
db.session.add(Microsoft)

from werkzeug.security import generate_password_hash
Nikita = User(email='bragin.kit@gmail.com', name='Nikita', password=generate_password_hash('qwerty', method='sha256'))
db.session.add(Nikita)

First = Shareholder(user_id=1, company_id=1, order_share_ammount=100, order_share_price=120)
Second = Shareholder(user_id=1, company_id=2, order_share_ammount=150, order_share_price=110)
db.session.add(First)
db.session.add(Second)
db.session.commit()

'''
