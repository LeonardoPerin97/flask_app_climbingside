#app/__init__.py

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy




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

    #with app.app_context():
    #    db.create_all() 


    #from app.models import Wall
    #with app.app_context():
        # Controlla se i dati iniziali devono essere inseriti
    #    if Wall.query.count() == 0:
    #        wall_a = Wall(name="A")
    #        wall_b = Wall(name="B")
    #        wall_c = Wall(name="C")
    #        wall_d = Wall(name="D")
    #        db.session.add(wall_a)
    #        db.session.add(wall_b)
    #        db.session.add(wall_c)
    #        db.session.add(wall_d)
    #        db.session.commit()


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

    
    
    return app
