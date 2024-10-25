#app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from statistics import mean
from collections import Counter
from datetime import datetime
from app.models import Route, User, user_route, Wall
from app.forms import RouteForm
from app.utils import display_grade_backend
from app.utils import save_route_picture
from app import db
import cloudinary
import cloudinary.uploader


routes = Blueprint('routes', __name__)


# ROUTES LIST
@routes.route('/routes')
def routes_list():
    
    sort_order = request.args.get('sort', 'default')
    # Base query for routes, including counting repetitions and calculating average score
    base_query = db.session.query(
        Route,
        func.count(user_route.c.route_id).label('repetitions'),
        func.coalesce(func.avg(user_route.c.score), 0).label('avg_score'),
        func.coalesce(func.avg(user_route.c.proposed_grade), -1).label('avg_proposed_grade')
    ).outerjoin(user_route, Route.id == user_route.c.route_id) \
     .group_by(Route.id)
    # Modify the query based on the selected sort order
    if sort_order == 'asc':
        routes = base_query.order_by(Route.grade).all()
    elif sort_order == 'repetitions':
        routes = base_query.order_by(func.count(user_route.c.route_id).desc()).all()
    elif sort_order == 'avg_score':
        routes = base_query.order_by(func.coalesce(func.avg(user_route.c.score), 0).desc()).all()
    elif sort_order == 'alph':
        routes = base_query.order_by(Route.name).all()
    else:
        routes = base_query.order_by(Route.id).all()
        
    # Unpack routes to add repetitions and avg_score fields
    routes_list = []
    for route, repetitions, avg_score, avg_proposed_grade in routes:
        # Check if the current user has added a repetition for this route
        user_has_done = False
        if current_user.is_authenticated:
            # Query the user_route table to check if there's an entry for the current user and this route
            user_has_done = db.session.query(user_route).filter_by(
                user_id=current_user.id,
                route_id=route.id
            ).count() > 0
        route_data = {
            'id': route.id,
            'name': route.name,
            'wall_id': route.wall_id,
            'wall': route.wall.name,
            'grade': route.grade,
            'repetitions': repetitions,
            'avg_score': avg_score,
            'avg_proposed_grade': display_grade_backend(avg_proposed_grade),
            'done': user_has_done
        }
        routes_list.append(route_data)

    # Query per contare le occorrenze di ogni Route.grade
    allroutes = Route.query.all()
    nroutes=len(allroutes)
    grades = [route.grade for route in allroutes]
    french_grades = [
    "4a", "4a+", "4b", "4b+", "4c", "4c+", 
    "5a", "5a+", "5b", "5b+", "5c", "5c+", 
    "6a", "6a+", "6b", "6b+", "6c", "6c+",
    "7a", "7a+", "7b", "7b+", "7c", "7c+",
    "8a", "8a+", "8b", "8b+", "8c", "8c+",
    "9a", "9a+", "9b", "9b+", "9c"
    ]
    grade_frequencies = dict(Counter(grades))
    # Ensure all grades in the range have a frequency (fill missing with 0)
    grade_distribution = {grade: grade_frequencies.get(grade, 0) for grade in french_grades}
    
    return render_template('routes/routes_list.html', routes=routes_list, sort_order=sort_order, grade_distribution=grade_distribution, nroutes=nroutes)




@routes.route('/add_route', methods=['GET', 'POST'])
@login_required  # Only logged-in users can add routes
def add_route():
    form = RouteForm()
    form.wall.choices = [(wall.id, wall.name) for wall in Wall.query.all()]
    if form.validate_on_submit():
        new_route = Route(name=form.name.data, grade=form.grade.data, wall_id = form.wall.data)
        db.session.add(new_route)
        db.session.commit()
        flash('Route has been added!', 'success')
        return redirect(url_for('routes.routes_list'))
    return render_template('routes/add_route.html', form=form) # Redirect to the route list page after submission



@routes.route('/delete_routes')
@login_required
def routes_list_with_delete():
    routes = Route.query.all()
    return render_template('routes/routes_list_with_delete.html', routes=routes)



@routes.route('/delete_routes/<int:route_id>', methods=['POST'])
@login_required
def delete_route(route_id):
    route = Route.query.get_or_404(route_id)  # Fetch the route
    db.session.delete(route)
    db.session.commit()
    flash(f'You have deleted {route.name}.', 'success')
    return redirect(url_for('routes.routes_list'))



# ROUTE PAGE
@routes.route('/routes/<int:route_id>', methods=['GET', 'POST'])
def route_page(route_id):
    route = Route.query.get_or_404(route_id)
    # Query to fetch all users, along with their proposed grade and score
    user_data = db.session.execute(
        user_route.select().where(user_route.c.route_id == route_id).order_by(desc(user_route.c.date))
    ).fetchall()
    # Format the data into a list of dictionaries (or a more complex object if needed)
    users_with_grades = []
    current_user_repetition = None
    for user_entry in user_data:
        user = User.query.get(user_entry.user_id)  # Fetch the user details
        # If the user is the current user, store their repetition details
        if current_user.is_authenticated and user.id == current_user.id:
            current_user_repetition = {
                'proposed_grade': user_entry.proposed_grade,
                'score': user_entry.score,
                'date': user_entry.date
            }
        users_with_grades.append({
            'user': user,
            'proposed_grade': user_entry.proposed_grade,
            'score': user_entry.score,
            'date': user_entry.date
        }) 
    n_rep = len(users_with_grades)
    # Extract the scores and proposed grades
    scores = [float(user_entry.score) for user_entry in user_data]
    grades = [float(user_entry.proposed_grade) for user_entry in user_data]
    # Calculate averages (if there are scores/grades)
    avg_score = mean(scores) if scores else 0
    avg_proposed_grade = mean(grades) if grades else 0
    min_grade = int(min(grades)) if grades else 0
    max_grade = int(max(grades)) if grades else 0
    # Create a full list of grades from min_grade to max_grade
    all_grades = list(range(min_grade, max_grade + 1))  
    # Count the frequency of each proposed grade
    grade_frequencies = dict(Counter(grades))
    # Ensure all grades in the range have a frequency (fill missing with 0)
    full_grade_frequencies = {grade: grade_frequencies.get(grade, 0) for grade in all_grades}
    grade_labels = {int(grade): display_grade_backend(int(grade)) for grade in all_grades}

    if request.method == 'POST' and current_user.is_authenticated:
        action = request.form.get('action')  # Identify if it's an add or edit action
        if action == 'add' or action == 'edit':
            score = request.form.get('score')  # Get the score from the form
            proposed_grade = request.form.get('proposed_grade')  # Get the proposed_grade from the form
            date = request.form.get('date')  # Get the date from the form
            
            # Validate the date (optional: handle errors if the date is not valid)
            try:
                date = datetime.strptime(date, '%Y-%m-%d')  # Convert string to datetime object
            except ValueError:
                flash('Invalid date format. Please select a valid date.', 'danger')
                return redirect(url_for('routes.route_page', route_id=route_id))
            # Validate form data
            if score is None or proposed_grade is None:
                flash('Score and proposed grade are required.', 'danger')
                return redirect(url_for('routes.route_page', route_id=route_id))
            # Convert proposed_grade to int for processing
            try:
                proposed_grade = int(proposed_grade)
                score = int(score)
            except ValueError:
                flash('Invalid input for score or proposed grade.', 'danger')
                return redirect(url_for('routes.route_page', route_id=route_id))
            
            # ADD
            if action == 'add':
                if current_user not in route.users:
                    #route.users.append(current_user)
                    db.session.execute(user_route.insert().values(user_id=current_user.id, route_id=route.id, score=score, proposed_grade=proposed_grade, date=date))
                    db.session.commit()
                    flash(f'{current_user.username} added to {route.name}!', 'success')
                else:
                    flash(f'You have already added your repetition of {route.name}.', 'info')
            # EDIT
            elif action == 'edit':  # Edit the existing repetition
                # Update the user's repetition in the database
                db.session.execute(user_route.update().where(
                    (user_route.c.user_id == current_user.id) & 
                    (user_route.c.route_id == route.id)
                ).values(score=score, proposed_grade=proposed_grade, date=date))
                db.session.commit()
                flash(f'Your repetition of {route.name} has been updated!', 'success')
            return redirect(url_for('routes.route_page', route_id=route_id))

        elif action == 'add_image':
            if 'image' in request.files:
                image_file = request.files['image']  # Ottieni il file immagine dal form
                if image_file:
                    image_url = save_route_picture(image_file)  # Funzione che carica su Cloudinary
                    route.image_file = image_url  # Salva l'URL dell'immagine nel database
                    db.session.commit()
                    
    return render_template('routes/route_page.html', route=route, users_with_grades=users_with_grades, avg_score=avg_score, avg_proposed_grade=avg_proposed_grade, full_grade_frequencies=full_grade_frequencies,grade_labels=grade_labels, n_rep=n_rep, current_user_repetition=current_user_repetition)



@routes.route('/routes/<int:route_id>/remove_rep', methods=['POST'])
@login_required
def remove_route_rep(route_id):
    route = Route.query.get_or_404(route_id)  # Fetch the route
    # Check if the user is part of this route via the user_route table
    user_route_entry = db.session.execute(
        user_route.select().where(user_route.c.user_id == current_user.id).where(user_route.c.route_id == route.id)
    ).fetchone()
    if user_route_entry:
        # Delete the user_route entry from the association table
        db.session.execute(
            user_route.delete().where(user_route.c.user_id == current_user.id).where(user_route.c.route_id == route.id)
        )
        db.session.commit()
        flash(f'You have removed {route.name}.', 'success')
    else:
        flash('You cannot remove this route because you are not associated with it.', 'danger')
    return redirect(url_for('routes.route_page', route_id=route.id))


@routes.route('/routes/<int:route_id>/delete_image', methods=['POST'])
@login_required
def delete_image(route_id):
    route = Route.query.get_or_404(route_id)

    if request.method == 'POST' and 'delete_image' in request.form:
        # Se l'utente ha caricato un'immagine
        if route.image_file:
            # (Facoltativo) Elimina l'immagine da Cloudinary
            # Estrai il public_id dall'URL dell'immagine su Cloudinary, se desideri eliminare anche dal cloud
            public_id = route.image_file.split('/')[-1].split('.')[0]  # Ottiene l'ID pubblico
            cloudinary.uploader.destroy(public_id)  # Cancella l'immagine da Cloudinary

            # Imposta il campo dell'immagine a None o al valore predefinito (es. 'default.jpg')
            route.image_file = None #'default.jpg'  # O None, se non vuoi avere un'immagine predefinita

            # Aggiorna il database
            db.session.commit()

            flash('Immagine eliminata con successo!', 'success')
        else:
            flash('Nessuna immagine da eliminare.', 'warning')

    return redirect(url_for('routes.route_page', route_id=route_id))








# WALLS LIST
@routes.route('/walls')
def walls_list():

    walls = Wall.query.all()
    
    walls_list = []

    for wall in walls:

        n_reps=0
        for route in wall.routes:
            n_reps+=len(route.users)

        wall_data = {
            'id': wall.id,
            'name': wall.name,
            'n_routes': len(wall.routes),
            'n_reps': n_reps
        }
        walls_list.append(wall_data)
        
        
    return render_template('routes/walls_list.html',walls=walls_list)




# WALL PAGE
@routes.route('/walls/<int:wall_id>')
def wall_page(wall_id):

    wall = Wall.query.filter_by(id=wall_id).first()

    n_routes=len(wall.routes)
    n_reps=0
    for route in wall.routes:
        n_reps+=len(route.users)

    sort_order = request.args.get('sort', 'default')
    # Base query for routes, including counting repetitions and calculating average score
    base_query = db.session.query(
        Route,
        func.count(user_route.c.route_id).label('repetitions'),
        func.coalesce(func.avg(user_route.c.score), 0).label('avg_score'),
        func.coalesce(func.avg(user_route.c.proposed_grade), -1).label('avg_proposed_grade')
    ).outerjoin(user_route, Route.id == user_route.c.route_id) \
    .filter(Route.wall_id == wall_id) \
    .group_by(Route.id)
    # Modify the query based on the selected sort order
    if sort_order == 'asc':
        routes = base_query.order_by(Route.grade).all()
    elif sort_order == 'repetitions':
        routes = base_query.order_by(func.count(user_route.c.route_id).desc()).all()
    elif sort_order == 'avg_score':
        routes = base_query.order_by(func.coalesce(func.avg(user_route.c.score), 0).desc()).all()
    else:
        routes = base_query.order_by(Route.id).all()
    # Unpack routes to add repetitions and avg_score fields
    routes_list = []
    for route, repetitions, avg_score, avg_proposed_grade in routes:
        # Check if the current user has added a repetition for this route
        user_has_done = False
        if current_user.is_authenticated:
            # Query the user_route table to check if there's an entry for the current user and this route
            user_has_done = db.session.query(user_route).filter_by(
                user_id=current_user.id,
                route_id=route.id
            ).count() > 0
        route_data = {
            'id': route.id,
            'name': route.name,
            'wall_id': route.wall_id,
            'wall': route.wall.name,
            'grade': route.grade,
            'repetitions': repetitions,
            'avg_score': avg_score,
            'avg_proposed_grade': display_grade_backend(avg_proposed_grade),
            'done': user_has_done
        }
        routes_list.append(route_data)

    allroutes = db.session.query(Route).filter(Route.wall_id == wall_id).group_by(Route.id)
    grades = [route.grade for route in allroutes]
    french_grades = [
    "4a", "4a+", "4b", "4b+", "4c", "4c+", 
    "5a", "5a+", "5b", "5b+", "5c", "5c+", 
    "6a", "6a+", "6b", "6b+", "6c", "6c+",
    "7a", "7a+", "7b", "7b+", "7c", "7c+",
    "8a", "8a+", "8b", "8b+", "8c", "8c+",
    "9a", "9a+", "9b", "9b+", "9c"
    ]
    grade_frequencies = dict(Counter(grades))
    # Ensure all grades in the range have a frequency (fill missing with 0)
    grade_distribution = {grade: grade_frequencies.get(grade, 0) for grade in french_grades}
    
    return render_template('routes/wall_page.html', wall=wall,n_routes=n_routes,n_reps=n_reps, routes=routes_list, sort_order=sort_order, grade_distribution=grade_distribution)

