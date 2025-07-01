from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gps_utils import get_gps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

photos = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['photo']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        gps = get_gps(filepath)
        photos.append({
            'filename': filename,
            'gps': gps
        })

    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', photos=photos)

if __name__ == '__main__':
    app.run(debug=True)
