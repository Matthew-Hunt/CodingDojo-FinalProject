from flask_app import app
from flask import flash, render_template, redirect, request, session, url_for
from flask_app.models.project import Projects
from flask_app.models.user import User
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = os.path.abspath('C:/Users/Matty/OneDrive/Desktop/Extras/CodingDojo/Course_Work/Proj&Algo/final_project/flask_app/static/user_img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        'id': session['user_id']
    }
    return render_template('dashboard.html', user=User.get_one_by_id(data), projects=Projects.get_all())

@app.route('/dashboard/myprojects')
def myprojects():
    if 'user_id' not in session:
        return redirect('/logout')
    user_id = {
        "user_id": session['user_id'],
        "id": session['user_id']
    }
    return render_template("dashboard.html", projects=Projects.get_all_by_one_user(user_id), user=User.get_one_by_id(user_id))

@app.route('/dashboard/myfavorites')
def myfavoriteprojects():
    if 'user_id' not in session:
        return redirect('/logout')
    user_id = {
        "user_id": session['user_id'],
        "id": session['user_id']
    }
    return render_template("dashboard.html", projects=Projects.get_all_favorites_by_one_user(user_id), user=User.get_one_by_id(user_id))

@app.route('/dashboard/mysearch', methods=['POST'])
def mysearch():
    if 'user_id' not in session:
        return redirect('/logout')
    user_id = {
        "user_id": session['user_id'],
        "id": session['user_id']
    }
    data = {
        "skill_level": request.form["skill_level"],
        "type": request.form["type"],
    }
    return render_template("dashboard.html", projects=Projects.get_all_projects_by_user_search(data), user=User.get_one_by_id(user_id))

@app.route('/project/<int:id>')
def project(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    user_data = {
        "id": session['user_id']
    }
    return render_template("view.html", project=Projects.get_one_project_by_id(data), user=User.get_one_by_id(user_data))

@app.route('/favorite/<int:project_id>/<int:user_id>')
def add_favorite(user_id, project_id):
    data = {
        "project_id": project_id,
        "user_id": user_id
    }
    Projects.add_favorite(data)
    print("REQUEST.REFERRER", request.referrer)
    return redirect(f"{request.referrer}#{project_id}")

@app.route('/unfavorite/<int:project_id>/<int:user_id>')
def remove_favorite(user_id, project_id):
    data = {
        "project_id": project_id,
        "user_id": user_id
    }
    Projects.destroy_favorite(data)
    print("REQUEST.REFERRER", request.referrer)
    return redirect(f"{request.referrer}#{project_id}")

@app.route('/new')
def new():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": session['user_id']
    }
    return render_template("create.html", user=User.get_one_by_id(data))

@app.route('/create/project', methods=['POST'])
def create():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Projects.validate_project_form(request.form):
        if not Projects.validate_project_image(request.files):
            return redirect('/new')
    file = request.files['ProjectImg']
    if file:
        filename = secure_filename(file.filename)
        image_path = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("IMAGE VALIDATION - File saved here:", image_path)
    data = {
        "project_name": request.form["project_name"],
        "skill_level": request.form["skill_level"],
        "type": request.form["type"],
        "description": request.form["description"],
        "image_path": image_path,
        "user_id": session["user_id"]
    }
    Projects.save(data)
    return redirect('/dashboard')

@app.route('/edit/<int:id>')
def edit_form(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    user_data = {
        "id": session['user_id']
    }
    return render_template("edit.html", project=Projects.get_one_project_by_id(data), user=User.get_one_by_id(user_data))

@app.route('/update/project', methods=['POST'])
def update_form():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Projects.validate_project_form(request.form):
        return redirect(f'/edit/{request.form["id"]}')
    data = {
        "project_name": request.form["project_name"],
        "skill_level": request.form["skill_level"],
        "type": request.form["type"],
        "description": request.form["description"],
        "id": request.form["id"]
    }
    Projects.update_form(data)
    return redirect(f'/project/{request.form["id"]}')

@app.route('/edit/<int:id>/image')
def edit_image(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    user_data = {
        "id": session['user_id']
    }
    return render_template("edit_image.html", project=Projects.get_one_project_by_id(data), user=User.get_one_by_id(user_data))

@app.route('/update/project/image', methods=['POST'])
def update_image():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Projects.validate_project_image(request.files):
        return redirect(f'/edit/{request.form["id"]}/image')
    file = request.files['ProjectImg']
    print("FILE = REQUEST.FILES", file)
    if file:
        filename = secure_filename(file.filename)
        image_path = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("IMAGE VALIDATION - File saved here:", image_path)
    data = {
        "image_path": image_path,
        "id": request.form["id"]
    }
    Projects.update_image(data)
    return redirect(f'/edit/{request.form["id"]}')

@app.route('/destroy/project/<int:id>')
def destroy(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    Projects.destroy(data)
    return redirect("/dashboard")