from multiprocessing import allow_connection_pickling
from operator import truediv
from sqlite3 import connect
from unittest import result
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user
from flask import flash
import os
from werkzeug.utils import secure_filename
ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'} #


class Projects:
    db = "gamedev"

    def __init__(self, data):
        self.id = data['id']
        self.project_name = data['project_name']
        self.skill_level = data['skill_level']
        self.type = data['type']
        self.description = data['description']
        self.image_path = data['image_path']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.user = None
        self.favorited_by = set()

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM projects LEFT JOIN favorites on projects.id = favorites.project_id;"
        results = connectToMySQL(cls.db).query_db(query)
        project_ids = set()
        projects = []
        for i in range(len(results)):
            this_id = results[i]["id"]
            user_id = results[i]["favorites.user_id"]
            if this_id not in project_ids:
                project_ids.add(this_id)
                project = cls(results[i])
                if user_id:
                    project.favorited_by.add(user_id)
                projects.append(project)
            else:
                if projects[-1].id == this_id:
                    ref_idx = len(projects) - 1
                else:
                    for x in range(len(projects)):
                        if projects[x].id == this_id:
                            ref_idx = x
                            break
                if user_id:
                    projects[ref_idx].favorited_by.add(user_id)
        return projects

    @classmethod
    def get_all_by_one_user(cls, data):
        query = "SELECT * FROM projects LEFT JOIN favorites on projects.id = favorites.projects_id WHERE projects.user_id = %(user_id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        if not results:
            return []

        project_ids = set()
        projects = []
        for i in range(len(results)):
            this_id = results[i]["id"]
            user_id = results[i]["favorites.user_id"]
            if this_id not in project_ids:
                project_ids.add(this_id)
                project = cls(results[i])
                if user_id:
                    project.favorited_by.add(user_id)
                projects.append(project)
            else:
                if projects[-1].id == this_id:
                    ref_idx = len(projects) - 1
                else:
                    for x in range(len(projects)):
                        if projects[x].id == this_id:
                            ref_idx = x
                            break
                if user_id:
                    projects[ref_idx].favorited_by.add(user_id)
        return projects

    @classmethod
    def get_all_favorites_by_one_user(cls, data):
        query = "SELECT * FROM projects LEFT JOIN favorites on projects.id = favorites.project_id WHERE favorites.user_id= %(user_id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        project_ids = set()
        projects = []
        for i in range(len(results)):
            this_id = results[i]["id"]
            user_id = results[i]["favorites.user_id"]
            if this_id not in project_ids:
                project_ids.add(this_id)
                project = cls(results[i])
                if user_id:
                    project.favorited_by.add(user_id)
                projects.append(project)
            else:
                if projects[-1].id == this_id:
                    ref_idx = len(projects) - 1
                else:
                    for x in range(len(projects)):
                        if projects[x].id == this_id:
                            ref_idx = x
                            break
                if user_id:
                    projects[ref_idx].favorited_by.add(user_id)
        return projects

    @classmethod
    def get_one_project_by_id(cls, data):
        query = "SELECT * FROM projects LEFT JOIN users ON projects.user_id = users.id WHERE projects.id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        one_project = cls(results[0])
        user_data = {
            "id": results[0]["users.id"],
            "username": results[0]["username"],
            "email": "hidden",
            "password": "hidden",
            "created_at": "hidden",
            "updated_at": "hidden"
        }
        one_user = user.User(user_data)
        one_project.user = one_user
        return one_project

    @classmethod
    def add_favorite(cls, data):
        query = "INSERT INTO favorites (post_id,user_id) VALUES (%(post_id)s,%(user_id)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def destroy_favorite(cls, data):
        query = "DELETE FROM favorites WHERE user_id=%(user_id)s AND post_id=%(post_id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def save(cls, data):
        query = "INSERT INTO projects (project_name, skill_level, type, description, image_path, user_id) VALUES (%(project_name)s, %(skill_level)s, %(type)s, %(description)s, %(image_path)s, %(user_id)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def update_form(cls, data):
        query = "UPDATE projects SET project_name=%(project_name)s,skill_level=%(skill_level)s,type=%(type)s,description=%(description)s,updated_at=NOW() WHERE id=%(id)s;"
        print(query)
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def update_image(cls, data):
        query = "UPDATE projects SET image_path=%(image_path)s,updated_at=NOW() WHERE id=%(id)s;"
        print(query)
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def destroy(cls, data):
        query = "DELETE FROM projects WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS

    @staticmethod
    def validate_project_form(project):
        is_valid = True
        if len(project['project_name']) < 3:
            is_valid = False
            flash("Project name must be at least 3 characters", "project_name")
        if "skill_level" not in project:
            is_valid = False
            flash("Please select a skill level", "skill_level")
        if "type" not in project:
            is_valid = False
            flash("Please select a type", "type")
        if len(project['description']) < 3:
            is_valid = False
            flash("Description must be at least 3 characters", "description")
        return is_valid

    @staticmethod
    def validate_project_image(devimage):
        is_valid = True
        file = devimage['ProjectImg']
        if file.filename == '':
            flash("No image selected. Please choose an image.", "image_path")
            print("IMAGE VALIDATION - No file selected. Blank field.")
            is_valid = False
        elif not Projects.allowed_file(file.filename):
            flash("Image must be a png, jpg, or jpeg file type.", "image_path")
            print("IMAGE VALIDATION - File type extension is invalid.")
            is_valid = False
        return is_valid