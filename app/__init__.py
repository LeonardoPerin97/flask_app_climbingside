#app/__init__.py

from flask import Flask, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api



# Inizializza SQLAlchemy senza passare subito l'app
db = SQLAlchemy()

# Initialize Flask-Login
login_manager = LoginManager()



def create_app():
    app = Flask(__name__)

    # Configurazione (es. caricamento config dal file config.py)
    #app.config.from_object('config.Config')
    # Configura l'app (esempio con una configurazione di database)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inizializza SQLAlchemy con l'istanza dell'app
    db.init_app(app)


    # Configuration Cloudinary (for routes images)       
    cloudinary.config( 
        cloud_name = "dptmtwlpr", 
        api_key = "486591569557458", 
        api_secret = "7gKXn4mBnFWWxZ-FkJ5wUsY-XWQ", # Click 'View API Keys' above to copy your API secret
        secure=True
    )

    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'

    from app.models import User
    # Definisci il user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context processor per rendere `current_user` disponibile nei template
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    from app.utils import display_grade_backend
    @app.context_processor
    def utility_processor():
        # Directly inject `display_grade_backend` into the context with the desired name
        return dict(display_grade=display_grade_backend)



    from app.home import home
    # Registra blueprint (routes)
    app.register_blueprint(home)

    from app.users import users
    app.register_blueprint(users)

    from app.routes import routes
    app.register_blueprint(routes)



    # Download database
    DB_FILE_PATH = os.path.join(app.instance_path, 'site.db')
    @app.route('/download-db')
    @login_required
    def download_db():
        try:
            # Controlla se il file esiste
            if os.path.exists(DB_FILE_PATH):
                # Utilizza send_file per inviare il file al client
                return send_file(DB_FILE_PATH, as_attachment=True, download_name='site.db')
            else:
                # Se il file non esiste, ritorna un errore 404
                abort(404)
        except Exception as e:
            print(f"Errore nel download del file: {e}")
            abort(500)

    
    
    return app
