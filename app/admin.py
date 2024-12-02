from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from app.models import Route, User, user_route, Wall
from app import db
from sqlalchemy import func, desc

admin_db = Blueprint('admin_db', __name__)










# FUNZIONI PER CREARE, MODIFICARE O ELIMINARE USERS, ROUTES E WALLS

###################################################################
def create_user(username, password):
    """Crea un nuovo utente nel database."""
    try:
        # Controlla se esiste già un utente con lo stesso username
        existing_user = db.session.query(User).filter_by(username=username).one_or_none()
        if existing_user:
            print(f"Un utente con username '{username}' esiste già con ID {existing_user.id}.")
            return
        # Crea e aggiungi il nuovo utente
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        print(f"Utente '{username}' creato con successo con ID {new_user.id}.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante la creazione dell'utente: {e}")


def update_user(user_id, new_username=None, new_password=None):
    """Aggiorna le informazioni di un utente."""
    try:
        # Trova l'utente per ID
        user = db.session.query(User).filter_by(id=user_id).one_or_none()
        if user:
            if new_username:
                user.username = new_username
            if new_password:
                user.password = new_password
            # Salva le modifiche
            db.session.commit()
            print(f"Utente {user.username} con ID {user_id} aggiornato con successo.")
        else:
            print(f"Utente con ID {user_id} non trovato.")
    except Exception as e:
        db.session.rollback()  # Annulla le modifiche in caso di errore
        print(f"Errore durante l'aggiornamento dell'utente: {e}")


def delete_user(user_id):
    """Elimina un utente dal database per ID."""
    try:
        # Trova l'utente per ID
        user = db.session.query(User).filter_by(id=user_id).one_or_none()
        if user:
            db.session.delete(user)
            db.session.commit()
            print(f"Utente '{user.username}' con ID {user_id} eliminato con successo.")
        else:
            print(f"Utente con ID {user_id} non trovato.")
    except Exception as e:
        db.session.rollback()  # Annulla le modifiche in caso di errore
        print(f"Errore durante l'eliminazione dell'utente: {e}")


###################################################################
def create_route(name, grade, wall_id, image_file=None):
    """Crea una nuova via nel database."""
    try:
        # Controlla se esiste già una via con lo stesso nome associato allo stesso muro
        existing_route = db.session.query(Route).filter_by(name=name, wall_id=wall_id).one_or_none()
        if existing_route:
            print(f"Una via con nome '{name}' per il muro con ID {wall_id} esiste già con ID {existing_route.id}.")
            return
        # Crea e aggiungi il nuovo percorso
        new_route = Route(name=name, grade=grade, wall_id=wall_id, image_file=image_file)
        db.session.add(new_route)
        db.session.commit()
        print(f"Via '{name}' creata con successo con ID {new_route.id}.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante la creazione della via: {e}")


def update_route(route_id, new_name=None, new_grade=None, new_wall_id=None):
    """Aggiorna le informazioni di una via."""
    try:
        route = db.session.query(Route).filter_by(id=route_id).one_or_none()
        if route:
            if new_name:
                route.name = new_name
            if new_grade:
                route.grade = new_grade
            if new_wall_id:
                route.wall_id = new_wall_id
            db.session.commit()
            print(f"Via '{route.name}' con ID {route_id} aggiornata con successo.")
        else:
            print(f"Via con ID {route_id} non trovata.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'aggiornamento della via: {e}")


def delete_route(route_id):
    """Elimina un percorso dal database per ID."""
    try:
        route = db.session.query(Route).filter_by(id=route_id).one_or_none()
        if route:
            db.session.delete(route)
            db.session.commit()
            print(f"Via '{route.name}' con ID {route_id} eliminata con successo.")
        else:
            print(f"Via con ID {route_id} non trovata.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'eliminazione della via: {e}")

###################################################################
def create_wall(name):
    """Crea un nuovo muro nel database se non esiste già."""
    try:
        # Controlla se esiste già un muro con lo stesso nome
        existing_wall = db.session.query(Wall).filter_by(name=name).one_or_none()
        if existing_wall:
            print(f"Un muro con il nome '{name}' esiste già con ID {existing_wall.id}.")
            return
        # Crea e aggiungi il nuovo muro se non esiste
        new_wall = Wall(name=name)
        db.session.add(new_wall)
        db.session.commit()
        print(f"Muro '{name}' creato con successo con ID {new_wall.id}.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante la creazione del muro: {e}")


def update_wall(wall_id, new_name=None):
    """Aggiorna le informazioni di un muro esistente nel database."""
    try:
        # Trova il muro per ID
        wall = db.session.query(Wall).filter_by(id=wall_id).one_or_none()
        if wall:
            # Aggiorna il nome se fornito
            if new_name:
                wall.name = new_name
            # Salva le modifiche
            db.session.commit()
            print(f"Muro con ID {wall_id} aggiornato con successo. Nuovo nome: '{wall.name}'.")
        else:
            print(f"Muro con ID {wall_id} non trovato.")
    except Exception as e:
        # Annulla le modifiche in caso di errore
        db.session.rollback()
        print(f"Errore durante l'aggiornamento del muro: {e}")


def delete_wall(wall_id):
    """Elimina un muro dal database per ID."""
    try:
        wall = db.session.query(Wall).filter_by(id=wall_id).one_or_none()
        if wall:
            db.session.delete(wall)
            db.session.commit()
            print(f"Muro '{wall.name}' con ID {wall_id} eliminato con successo.")
        else:
            print(f"Muro con ID {wall_id} non trovato.")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'eliminazione del muro: {e}")

###################################################################











@admin_db.route('/admin_db', methods=['GET', 'POST'])
@login_required
def admin_db_page():
    if not (current_user.id == 1 or current_user.id == 2):  
        flash("Access denied", "danger")
        return redirect(url_for('home'))  # Reindirizza alla home se non è admin
    
    # Recupera dati dal database per visualizzarli nel template
    users = db.session.query(User).all()
    walls = db.session.query(Wall).all()
    routes = db.session.query(Route).all()
    reps = db.session.query(user_route).all()


    if request.method == 'POST':
        # Determina l'operazione da eseguire in base ai dati inviati dal form
        action = request.form.get('action')
        
        # Creazione Utente
        if action == 'create_user':
            username = request.form.get('username')
            password = request.form.get('password')
            create_user(username, password)
        
        # Aggiornamento Utente
        elif action == 'update_user':
            user_id = int(request.form.get('user_id'))
            new_username = request.form.get('new_username')
            new_password = request.form.get('new_password')
            update_user(user_id, new_username, new_password)
        
        # Eliminazione Utente
        elif action == 'delete_user':
            user_id = int(request.form.get('user_id'))
            delete_user(user_id)
        
        # Creazione Muro
        elif action == 'create_wall':
            wall_name = request.form.get('wall_name')
            create_wall(wall_name)
        
        # Aggiornamento Muro
        elif action == 'update_wall':
            wall_id = int(request.form.get('wall_id'))
            new_name = request.form.get('new_wall_name')
            update_wall(wall_id, new_name)
        
        # Eliminazione Muro
        elif action == 'delete_wall':
            wall_id = int(request.form.get('wall_id'))
            delete_wall(wall_id)
        
        # Creazione Via
        elif action == 'create_route':
            route_name = request.form.get('route_name')
            grade = request.form.get('grade')
            wall_id = int(request.form.get('wall_id'))
            create_route(route_name, grade, wall_id)
        
        # Aggiornamento Via
        elif action == 'update_route':
            route_id = int(request.form.get('route_id'))
            new_name = request.form.get('new_route_name')
            new_grade = request.form.get('new_grade')
            new_wall_id = int(request.form.get('new_wall_id'))
            update_route(route_id, new_name, new_grade, new_wall_id)
        
        # Eliminazione Via
        elif action == 'delete_route':
            route_id = int(request.form.get('route_id'))
            delete_route(route_id)
        
        return redirect(url_for('admin_db.admin_db_page'))



    # Recupera i parametri di ricerca dalla query string
    search_name = request.args.get('search_name', '').strip()
    search_grade = request.args.get('search_grade', '').strip()
    # Applica i filtri di ricerca se specificati
    if search_name:
        routes = db.session.query(Route).filter(
            Route.name.ilike(f"{search_name}%") |
            Route.name.ilike(f"% {search_name}%")
            ).all()
    if search_grade:
        routes = db.session.query(Route).filter(Route.grade == search_grade).all()


    
    return render_template('admin_db_page.html', users=users, walls=walls, routes=routes, reps=reps, search_name=search_name)
