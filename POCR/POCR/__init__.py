import sqlite3
import os
from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, g
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

__author__ = 'ittiRehan'

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , flaskr.py

UPLOAD_FOLDER = "POCR/Uploads/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'pocr.db'),
    SECRET_KEY='itti rehan',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route("/")
def homepage():
    return render_template("index.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/extract", methods=['GET', 'POST'])
def extractPage():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template("upload.html")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    path_to_file =os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(path_to_file)
    im = Image.open(path_to_file,'r')
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\HP\\Tesseract-OCR\\tesseract.exe'

    text = pytesseract.image_to_string(im, lang='eng')

    return text


@app.route("/contact")
def contactpage():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run()
