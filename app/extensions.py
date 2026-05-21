from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()