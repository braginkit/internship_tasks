from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from .models import User
from . import db

auth = Blueprint('auth', __name__)

class Form(FlaskForm):
    buy_flag = ''

@auth.route('/login')
def login():
    form = Form(request.form)
    return render_template('login.html', form=form)

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    form = Form(request.form)

    if not user and not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return render_template('login.html', form=form)

    login_user(user, remember=remember)
    
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    form = Form(request.form)
    return render_template('signup.html', form=form)

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    form = Form(request.form)

    if email == '' or name == ''  or password == '' :
        flash('Please fill in every field.')
        return render_template('signup.html', form=form)
    else:

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists.')
            return redirect(url_for('auth.signup'))

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()

        form = Form(request.form)
        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    form = Form(request.form)
    return redirect(url_for('main.index'))
