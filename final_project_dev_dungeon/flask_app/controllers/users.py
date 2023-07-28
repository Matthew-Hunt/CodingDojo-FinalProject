from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from flask_app import app
from flask_app.models.project import Projects
from flask_app.models.user import User

bcrypt = Bcrypt(app)


@app.route('/regcheck', methods=['POST'])
def register():
    if not User.validate_register(request.form):
        return redirect('/')

    data = {
        "username": request.form['username'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password'])
    }
    user_id = User.save(data)
    session['user_id'] = user_id
    return redirect('/dashboard')


@app.route('/login', methods=['POST'])
def login():
    user = User.get_one_by_email(request.form)
    if not user or not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid email or password", "login")
        return redirect('/')

    session['user_id'] = user.id
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')