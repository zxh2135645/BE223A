from flask import Flask, render_template, request, make_response, jsonify
from flask import Markup, redirect
from flask_bootstrap import Bootstrap
from flask_misaka import Misaka
import os
import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
import livedemo as lvdm
from app_calendar import *
from datetime import datetime,timedelta
import markdown
from timeslot_chart import *
from read_db import filt_shows

# Demo form
import numpy as np
#import xgboost as xgb
import pickle


content = ""
with open("./data/ML_Analysis.md", "r") as f:
     content = f.read()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'iridescent'
bootstrap = Bootstrap(app)
Misaka(app) # To use markdown in the template


@app.route('/Analytics')
def analytics():
    contents = content
    contents = Markup(markdown.markdown(contents))
    return render_template('home.html',content = contents)
    #return render_template('ML_Analysis.html')

@app.route('/for_orgcode_charts_json')
def for_orgcode_charts(feature='OrgCode'):
    show_df, noshow_df = filt_shows()
    show_labels = [0] * len(show_df.index) + [1] * len(noshow_df.index)
    info = pd.concat([show_df, noshow_df], axis=0)
    info['Labels'] = show_labels
    labels = sorted(info[feature].unique())
    show = []
    noshow = []

    for f in labels:
        completed_count = list(info[info[feature] == f]['Labels'] == 0).count(True)
        noshow_count = list(info[info[feature] == f]['Labels'] == 1).count(True)
        show.append(completed_count)
        noshow.append(noshow_count)
    data = dict()

    percent_show = []
    percent_noshow = []
    for i, s in enumerate(show):
        total = s + noshow[i]
        if total == 0:
            percent_show.append(s)
            percent_noshow.append(noshow[i])
        else:
            percent_show.append(s/total)
            percent_noshow.append(noshow[i]/total)

    data['Show'] = percent_show
    data['NoShow'] = percent_noshow

    stack = []
    for key in data:
        stack.append(key)

    data['stack'] = stack
    data['labels'] = labels
    return jsonify(result = data)

@app.route('/for_modality_charts_json')
def for_modality_charts(feature='Modality'):
    show_df, noshow_df = filt_shows()
    show_labels = [0] * len(show_df.index) + [1] * len(noshow_df.index)
    info = pd.concat([show_df, noshow_df], axis=0)
    info['Labels'] = show_labels
    orgcode = request.args.get('orgcode')
    if orgcode == 'Choose':
        data = dict()
    else:
        data = dict()

        labels = sorted(info[feature].unique())
        show = []
        noshow = []

        for f in labels:
            info_temp = info[info['OrgCode'] == orgcode]
            completed_count = list(info_temp[info_temp[feature] == f]['Labels'] == 0).count(True)

            noshow_count = list(info_temp[info_temp[feature] == f]['Labels'] == 1).count(True)
            show.append(completed_count)
            noshow.append(noshow_count)

        percent_show = []
        percent_noshow = []
        for i, s in enumerate(show):
            total = s + noshow[i]
            if total == 0:
                percent_show.append(s)
                percent_noshow.append(noshow[i])
            else:
                percent_show.append(s/total)
                percent_noshow.append(noshow[i]/total)

        data['Show'] = percent_show
        data['NoShow'] = percent_noshow
        stack = []
        for key in data:
            stack.append(key)

        data['stack'] = stack
        data['labels'] = labels

    return jsonify(result = data)

@app.route('/calendar')
def calendar():
    return render_template("calendar.html")


# Live demo route
#@app.route('/livedemo', methods=['GET', 'POST'])
#def livedemo():
#    # form instance
#    form = lvdm.DemoForm()
    # Initialize variables
#    prediction_html_table = None
#    predicted = False
#    if form.validate_on_submit():
        # Extract form data
#        age, gender, modality, orgcode = lvdm.process_demo_form(form)
        # Send data to get prediction table
#        prediction_html_table = lvdm.predict_week(age, gender, modality, orgcode)
#        predicted = True

# Load hospital_map
hospital_map = pickle.load(open("./data/hospital_map.dat", "rb"))

@app.route('/modalities_json')
def modalities_json():
    '''
    Gets orgcode returns modalities
    '''
    orgcode = request.args.get('orgcode')
    if orgcode == 'Choose':
        modalities = ['Choose']
    else:
        modalities = ['Choose']+list(hospital_map[orgcode].keys())
    return jsonify(result = modalities )

@app.route('/departments_json')
def departments_json():
    '''
    Gets orgcode and modality returns departments
    '''
    orgcode = request.args.get('orgcode')
    modality = request.args.get('modality')
    departments = ['Choose']+hospital_map[orgcode][modality]
    return jsonify(result = departments )

@app.route('/calendar_json')
def calendar_json():
    orgcode = request.args.get('orgcode')
    modality = request.args.get('modality')
    dept = request.args.get('departmentcode')
    # The initial date on the week calendar hard-coded, to be updated when data are current
    initial_date = datetime(3246,12,10)
    table_data, days, ts_times = generate_timeslots(orgcode, modality, dept, initial_date)

    ts_data = timeslots_for_charts(orgcode, modality, dept, initial_date)

    prev_week1 = initial_date - timedelta(days = 7)
    ts_data2 = timeslots_for_charts(orgcode, modality, dept, prev_week1)

    columns_names = [' ']+ days
    table = {
        'columns_names' : columns_names,
        'row_names': ts_times,
        'rows' : table_data,
        'ts_data': ts_data,
        'ts_data2': ts_data2
    }
    return jsonify(result = table)

@app.route('/_patient_json')
def patient_json():
    exam_id = request.args.get('exam_id')
    # Look in database for the exam_id and pull information of the patient
    patient_info = {
        'name': "John",
        'telephone': 1112223333,
        'email': 'john@gmail.com',
        'gender': 'Male',
        'age': 83
    }
    return jsonify(result = patient_info)



# Retrieve data from database
# Let's set up just a list for now
orgcodes = ['Choose']+list(hospital_map.keys())
orgcodes_choices = [(org, org) for org in orgcodes]
class FiltersForm(FlaskForm):
    orgcode = SelectField('Organization Code', choices = orgcodes_choices)
    modality = SelectField('Exam Modality', choices = [('Choose', 'Choose')])
    departmentcode = SelectField('Department Code', choices = [('Choose', 'Choose')])

class PatientForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices = [('1', 'Male'), ('0', 'Female')])
    submit = SubmitField('Submit')

@app.route('/')
def dashboard():
    form = FiltersForm()
    patient_form = PatientForm()
    return render_template('dashboard.html', form =form)


@app.route('/_render_calendar')
def calendar_data():
    orgcode = 'ASM' #orgcode = request.args.get('orgcode')
    modality = 'CR' #modality = request.args.get('modality')
    timeslots, days = find_timeslots(orgcode, modality)
    return jsonify(timeslots = timeslots, days = days)

def find_timeslots(orgcode, modality):
    # Retrieve data from database
    # Let's set up just a list for now
    timeslots = ["08:00", "10.00", "15:00"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    return timeslots, days

def render_calendar(orgcode, modality):

    return None

#@app.route('/dropdown')
#def chart():
#    labels = ["January","February","March","April","May","June","July","August"]
#    values = [10,9,8,7,6,4,7,8]
#    return render_template('chart.html', values=values, labels=labels)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
