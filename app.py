from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gps_utils import get_gps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# This will act as temporary in-memory storage
photos = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['photo']
    project_name = request.form.get('project_name')
    notes = request.form.get('notes')

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        gps = get_gps(filepath)

        photos.append({
            'filename': filename,
            'filepath': filepath,
            'project_name': project_name,
            'notes': notes,
            'gps': gps
        })

    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', photos=photos)

@app.route('/compare')
def compare():
    # Use two sample images from static/uploads for now
    return render_template('compare.html', 
        before_image='static/uploads/before.jpg', 
        after_image='static/uploads/after.jpg'
    )

if __name__ == '__main__':
    app.run(debug=True)
