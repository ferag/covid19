from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from flask_oidc import OpenIDConnect
from wtforms import SelectField, TextField
from sqlalchemy import create_engine
import sqlite3
import pandas as pd

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_OPENID_REALM': 'http://localhost:5000/oidc_callback'
})
oidc = OpenIDConnect(app)

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
    if oidc.user_loggedin:
        return ('Hello, %s, <a href="/logged">See private</a> '
                '<a href="/logout">Log out</a>') % \
            oidc.user_getfield('email')
    else:
        return 'Welcome anonymous, <a href="/logged">Log in</a>'

@app.route('/logged')
@oidc.require_login
def logged():
    info = oidc.user_getinfo(['email', 'openid_id'])
    return render_template('logged.html', email=info.get('email'), openid_id=info.get('openid_id'))

@app.route('/logout')
def logout():
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'


@app.route('/results')
@oidc.require_login
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
@oidc.require_login
def training():
    error = ""
    edad, img_id, img = get_random_img() #get_random
    form = TrainingForm(request.form)

    if request.method == 'POST':
        type_of_diag = form.type_of_diag.data
        info = oidc.user_getinfo(['email', 'openid_id'])
        session['user_id'] = info.get('email')
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
    try:
        info = oidc.user_getinfo(['email', 'openid_id'])
        conn = sqlite3.connect('db/covid19.db')
        c = conn.cursor()
        print("SELECT COUNT(*) FROM users WHERE id='%s'" % (info.get('email')))
        x = c.execute("SELECT COUNT(*) FROM users WHERE id='%s'" % (info.get('email')))
        row = c.fetchone()
        if row[0] > 0:
            return render_template('training.html', form=form, message=error, edad=edad, img=img, img_id=img_id)
        else:
            return 'You are not an allowed user'
        conn.close()
    except Exception as e:
        conn.close()
        print(e)
        return 'Ooops!, <a href="/logged">Log in</a>'

# Run the application
app.run(debug=True)
