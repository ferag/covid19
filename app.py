from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import SelectField, TextField
from sqlalchemy import create_engine
import sqlite3
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'

BASE_PATH = '/home/aguilarf/sars-cov-2/AppTraining/examples-forms/'
IMG_FOLDER = '/static/img/'

def check_user_answer(id_image, user_answer):
    print("Select  id_image and get type")
    print("IF user answer is equal to image type")
    result = "Result is OK"
    print("IF not")
    result = "This image is type Patological (covid-19 compatible)"
    return result 

def get_random_img():
    conn = sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    x = c.execute("SELECT edad, id, codigo FROM images ORDER BY random() LIMIT 1;").fetchall()
    for row in x:
        img = IMG_FOLDER + row[2] +'.jpg'
        img_id = row[1]
        edad = row[0]
    conn.close()
    return edad, img_id, img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results')
def results():
    res = check_user_answer(session['messages']['id_image'], session['messages']['user_answer'])
    print(res)
    return render_template('results.html', res=res, image=session['messages']['img'])

class TrainingForm(Form):
 
    type_of_diag = SelectField(
        u'Type of Diagnosis',
        choices=[('pat_covid_com', 'Patological (covid-19 compatible)'),
                 ('pat_no_covid_com', 'Patological (NO covid-19 compatible)'),
                 ('non_pat', 'Non Patological')])
    

@app.route('/training', methods=['GET', 'POST'])
def training():
    error = ""
    edad, img_id, img = get_random_img() #get_random
    form = TrainingForm(request.form)

    if request.method == 'POST':
        type_of_diag = form.type_of_diag.data
        session['user_id'] = 'aguilarf'
        session['messages'] = {'id_image': img_id, 'img': img, 'user_answer' : form.type_of_diag.data}
        if len(type_of_diag) == 0:
            error = "Please supply data"
        else:
            try:
                print("Try insert")
                conn = sqlite3.connect('db/covid19.db')
                c = conn.cursor()
                print("INSERT INTO user_answers(user, image, answer) VALUES ('%s', %i, '%s')" % (session['user_id'], img_id, type_of_diag))
                c.execute("INSERT INTO user_answers(user, image, answer) VALUES ('%s', %i, '%s')" % (session['user_id'], img_id, type_of_diag))
                conn.commit()
                conn.close()
            except Exception as e:
                print("Ooops! We had a problem")
                print(e)
            return redirect(url_for('results'))

    return render_template('training.html', form=form, message=error, edad=edad, img=img, img_id=img_id)

# Run the application
app.run(debug=True)
