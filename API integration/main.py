from http.client import responses
from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import StringField, FloatField, validators
from sqlalchemy import desc
import requests
import json

from project.models import Town, Collections
from . import db


main = Blueprint('main', __name__)

class AddForm(FlaskForm):
    town_name = StringField('Town: ', [validators.Length(min=4, max=25)])
    flag = ''

class CalculateForm(FlaskForm):
    latitude = FloatField('Latitude: ', [validators.DataRequired()])
    longitude = FloatField('Longitude: ', [validators.DataRequired()])
    flag = ''


@main.route('/')
def index():
    class Form(FlaskForm): pass
    form = Form()
    return render_template('index.html', query=Town.query.all(), form=form)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    add_form = AddForm(request.form)
    calculate_form = CalculateForm(request.form)
    query_my_towns = Collections.query.filter_by(user_id=current_user.id).all()

    if (request.method == 'POST' and request.form['Submit'] == 'Add'):
        town_new = str(add_form.town_name.data)
        flag = Town.query.filter_by(name=town_new).first()
        if flag == None:

            response = requests.get('http://api.positionstack.com/v1/forward?access_key=5ee3d99cc5d592f8500e0c1d88e1f69d&query=' + town_new).content
            response = json.loads(response)
            cur_name = response["data"][0]["name"]
            cur_latitude = response["data"][0]["latitude"]
            cur_longitude = response["data"][0]["longitude"]

            NewTown = Town(name=cur_name, latitude=cur_latitude, longitude=cur_longitude)
            db.session.add(NewTown)
            db.session.commit()

            town_id = Town.query.filter_by(name=cur_name).first()
            NewCollection = Collections(user_id=current_user.id, town_id=town_id.id)
            db.session.add(NewCollection)
            db.session.commit()
            add_form.flag = 'Added in your collection'

        elif Collections.query.filter_by(user_id=current_user.id, town_id=flag.id).first() == None:
            NewCollection = Collections(user_id=current_user.id, town_id=flag.id)
            db.session.add(NewCollection)
            db.session.commit()
            add_form.flag = 'Added in your collection'
        else:
            add_form.flag = 'Already in your collection'

    query_calculations = []
    if (request.method == 'POST' and request.form['Submit'] == 'Calculate'):
        cur_latitude = float(calculate_form.latitude.data)
        cur_longitude = float(calculate_form.longitude.data)
        town_list = []
        town_list = Collections.query.filter_by(user_id=current_user.id).all()
        if len(town_list) < 2:
            calculate_form.flag = 'Add more towns to your collection'
        elif len(town_list) == 2:
            query_calculations.append(town_list[0].Town.name)
            query_calculations.append(town_list[1].Town.name)
        else:
            first_town_space = float('inf')
            second_town_space = float('inf')
            first_town_name = ''
            second_town_name = ''
            print(town_list)
            for cur in town_list:
                cur_space = ((cur.Town.latitude - cur_latitude)**2 + (cur.Town.longitude - cur_longitude)**2)**(0.5)
                print(cur_space)
                if cur_space < first_town_space:
                    second_town_space = first_town_space
                    second_town_name = first_town_name
                    first_town_space = cur_space
                    first_town_name = cur.Town.name
                elif cur_space < second_town_space:
                    second_town_space = cur_space
                    second_town_name = cur.Town.name
            print(first_town_name)
            print(second_town_name)
            query_calculations.append(first_town_name)
            query_calculations.append(second_town_name)

    return render_template('profile.html', name=current_user.name, query_my_towns=query_my_towns, add_form=add_form, calculate_form=calculate_form, query_calculations=query_calculations)
