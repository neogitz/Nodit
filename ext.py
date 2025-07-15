import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

UPLOAD_FOLDER = "static/uploads"

app = Flask(__name__)
app.config["SECRET_KEY"] = "Q4g_6L!p@92d#nmFz9B*!e2V%rLwZpMv"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///NodIt.db"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
migrate = Migrate(app, db)
