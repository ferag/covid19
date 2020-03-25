from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import SelectField, TextField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'

BASE_PATH = '/home/aguilarf/sars-cov-2/AppTraining/examples-forms/'
IMG_FOLDER = '/static/img/'

def check_user_answer(id_image, user_answer):
    print("Select id_image and get type")
    print("IF user answer is equal to image type")
    result = "Result is OK"
    print("IF not")
    result = "This image is type Patological (covid-19 compatible)"
    return result 

def get_random_img():
    img = IMG_FOLDER + 'wilson.jpg'
    img_id = 12312
    return img, img_id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results')
def results():
    res = check_user_answer(session['messages']['id_image'], session['messages']['user_answer'])
    print(res)
    return render_template('results.html', res=res, image=session['messages']['img'])

class TrainingForm(Form):
    img, img_id = get_random_img() #get_random
 
    type_of_diag = SelectField(
        u'Type of Diagnosis',
        choices=[('pat_covid_com', 'Patological (covid-19 compatible)'),
                 ('pat_no_covid_com', 'Patological (NO covid-19 compatible)'),
                 ('non_pat', 'Non Patological')])
    

@app.route('/training', methods=['GET', 'POST'])
def training():
    error = ""
    form = TrainingForm(request.form)

    if request.method == 'POST':
        type_of_diag = form.type_of_diag.data
        session['messages'] = {'id_image': form.img_id, 'img': form.img, 'user_answer' : form.type_of_diag.data}
        if len(type_of_diag) == 0:
            error = "Please supply data"
        else:
            return redirect(url_for('results'))

    return render_template('training.html', form=form, message=error)

# Run the application
app.run(debug=True)
