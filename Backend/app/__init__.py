from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_restful import Api
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect

import os

db = SQLAlchemy()
api = Api()
mail = Mail()
cors = CORS()
migrate = Migrate()
jwt = JWTManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Database Configurations
    if config_class is None:
        app.config.from_object(os.environ.get('FLASK_CONFIG_TYPE', 'Default'))
    else:
        app.config.from_object(config_class)
    
    
    
    # Initialization
    db.init_app(app)
    api.init_app(app)
    mail.init_app(app) 
    cors.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    csrf.init_app(app)
    
    # Blueprints resgistrations
    from app.auth.routes import auth_bp
    
    app.register_blueprint(auth_bp)
    
    return app