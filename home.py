#from flask import Flask
#from flask import render_template
#app = Flask(__name__)


#@app.route('/')
#def main_page():
   # my_titleicloud.com/find = 'EEG overeasy!'
    
#    return render_template('index.html', my_title='EEG overeasy!')

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

#importing our input form
from forms import inputForm
app = Flask(__name__)
app.secret_key = 'development key'

#UPLOAD_FOLDER = '/Users/tamarisk/Davis/pccnProject'
#ALLOWED_EXTENSIONS = set(['cnt', 'bdf', 'eeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

@app.route('/', methods = ['GET', 'POST'])
def main_page():
    form = inputForm()
   
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('index.html', form = form)
        else:
            return render_template('success.html')
    elif request.method == 'GET':
        return render_template('index.html', form = form)

if __name__ == '__main__':
    app.run(debug = True)