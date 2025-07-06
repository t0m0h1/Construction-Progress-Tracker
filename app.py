from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import json
import uuid
from gps_utils import get_gps  # assumes this returns lat/lon dict or None

# --- Config ---
UPLOAD_FOLDER = 'static/uploads'
DATA_FILE = 'projects.json'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# --- App setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = 'your-secret-key'  # change in production

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Load/Save JSON Data ---
def load_projects():
    # Load projects from JSON file if it exists
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_projects(data):
    # Save projects to JSON file
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# --- Allowed file check ---
def allowed_file(filename):
    # Check if the uploaded file has an allowed extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/')
def index():
    # Render the index page with loaded projects
    projects = load_projects()
    return render_template('index.html', projects=projects)

@app.route('/upload', methods=['POST'])
def upload():
    # Handle file upload and project data submission
    file = request.files.get('photo')
    project_name = request.form.get('project_name', '').strip()
    notes = request.form.get('notes', '').strip()

    if not file or not allowed_file(file.filename) or not project_name:
        flash('Please upload a valid image and enter a project name.')
        return redirect(url_for('index'))

    projects = load_projects()
    safe_project = secure_filename(project_name)
    project_folder = os.path.join(app.config['UPLOAD_FOLDER'], safe_project)
    os.makedirs(project_folder, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(project_folder, unique_filename)
    file.save(filepath)

    gps_data = get_gps(filepath)

    photo_data = {
        'filename': unique_filename,
        'filepath': f'uploads/{safe_project}/{unique_filename}',
        'notes': notes,
        'gps': gps_data
    }

    if project_name not in projects:
        projects[project_name] = []

    projects[project_name].append(photo_data)
    save_projects(projects)

    flash('Photo uploaded successfully.')
    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    # Render the gallery page with loaded projects
    projects = load_projects()
    return render_template('gallery.html', projects=projects)

@app.route('/compare_select')
def compare_select():
    # Render the comparison selection page with loaded projects
    projects = load_projects()
    return render_template('compare_select.html', projects=projects)

@app.route('/compare_project', methods=['POST'])
def compare_project():
    # Handle project comparison and render comparison page
    projects = load_projects()
    project = request.form.get('project')
    before = request.form.get('before_image')
    after = request.form.get('after_image')

    photos = projects.get(project, [])
    before_path = next((p['filepath'] for p in photos if p['filename'] == before), None)
    after_path = next((p['filepath'] for p in photos if p['filename'] == after), None)

    if not before_path or not after_path:
        flash("Selected images not found.")
        return redirect(url_for('compare_select'))

    return render_template('compare.html', before_image=before_path, after_image=after_path)

@app.route('/delete_photo', methods=['POST'])
def delete_photo():
    # Handle photo deletion from the project
    project = request.form.get('project')
    filename = request.form.get('filename')
    projects = load_projects()

    safe_project = secure_filename(project)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_project, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    if project in projects:
        projects[project] = [p for p in projects[project] if p['filename'] != filename]
        if not projects[project]:
            del projects[project]  # clean up empty projects

    save_projects(projects)
    flash("Image deleted.")
    return redirect(url_for('gallery'))

# Log in and sign up routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle user login
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Placeholder for authentication logic
        flash(f'Logged in as {email} (authentication not yet implemented)')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handle user signup
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Placeholder for account creation logic
        flash(f'Account created for {username} (signup not yet implemented)')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Handle user logout
    session.pop('user', None)
    flash("You’ve been logged out.")
    return redirect(url_for('index'))

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
