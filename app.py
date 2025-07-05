from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gps_utils import get_gps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Store projects and their photos
projects = {}

@app.route('/')
def index():
    return render_template('index.html', projects=projects)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['photo']
    project_name = request.form.get('project_name').strip()
    notes = request.form.get('notes')

    if file and project_name:
        safe_project = secure_filename(project_name)
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'], safe_project)
        os.makedirs(project_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = os.path.join(project_folder, filename)
        file.save(filepath)

        gps = get_gps(filepath)

        photo_data = {
            'filename': filename,
            'filepath': f'uploads/{safe_project}/{filename}',  # for use with url_for('static', ...)
            'notes': notes,
            'gps': gps
        }

        if project_name not in projects:
            projects[project_name] = []

        projects[project_name].append(photo_data)

    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', projects=projects)

@app.route('/compare_select')
def compare_select():
    return render_template('compare_select.html', projects=projects)

@app.route('/compare_project', methods=['POST'])
def compare_project():
    project = request.form.get('project')
    before = request.form.get('before_image')
    after = request.form.get('after_image')

    project_photos = projects.get(project, [])
    before_path = next((p['filepath'] for p in project_photos if p['filename'] == before), None)
    after_path = next((p['filepath'] for p in project_photos if p['filename'] == after), None)

    return render_template('compare.html',
                           before_image=before_path,
                           after_image=after_path)


@app.route('/delete_photo', methods=['POST'])
def delete_photo():
    project = request.form.get('project')
    filename = request.form.get('filename')
    safe_project = secure_filename(project)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_project, filename)

    # Remove from disk
    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove from memory
    if project in projects:
        projects[project] = [p for p in projects[project] if p['filename'] != filename]

    return redirect(url_for('gallery'))
