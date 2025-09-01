#app/users.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, logout_user, current_user
from collections import Counter
from sqlalchemy import func, desc, case
from app.forms import RegistrationForm, LoginForm
from app.models import User, Route, user_route
from app import db



users = Blueprint('users', __name__)



@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the username already exists
        existing_user = User.query.filter_by(username=form.username.data.strip()).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            session['message'] = ('danger', 'Username already exists. Please choose a different one.')
        else:
             # Create a new user and save to the database
            new_user = User(username=form.username.data, password=form.password.data.strip())
            db.session.add(new_user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('users.login'))
    return render_template('users/register.html', form=form)



@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Look up the user in the database
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home.homepage'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
            if user:
                session['message'] = ('danger', 'Wrong password.')
            else:
                session['message'] = ('danger', "Username doesn't exists.")
    return render_template('users/login.html', form=form)



@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home.homepage'))



# USER PAGE
@users.route('/users/<int:user_id>')
def user_page(user_id):
    user = User.query.get_or_404(user_id)  # Fetch the user by ID, or return 404 if not found
    routes = user.routes  # Get the routes that this user has added
    nreps=len(routes)
    # Get the sorting option from the request arguments (default to 'id')
    sort_by = request.args.get('sort_by', 'date')  # Default to 'id' if not specified

    # Sort the routes based on the selected criteria
    if sort_by == 'grade':
        routes = Route.query.join(user_route).join(User).filter(User.id == user_id).order_by(desc(Route.grade), desc(user_route.c.date), desc(user_route.c.id)).all() 
    elif sort_by == 'date':
        routes = Route.query.join(user_route).join(User).filter(User.id == user_id).order_by(desc(user_route.c.date), desc(user_route.c.id)).all()
    else:
        routes = Route.query.join(user_route).join(User).filter(User.id == user_id).order_by(Route.id).all()

        # Fetch proposed_grade and score for each route
    for route in routes:
        # Fetch the proposed_grade and score from user_route table
        user_route_data = db.session.query(user_route.c.proposed_grade, user_route.c.score, user_route.c.date).filter_by(route_id=route.id, user_id=user_id).first()
        if user_route_data:
            route.proposed_grade, route.score, route.date = user_route_data  # Unpack the tuple
        else:
            route.proposed_grade, route.score, route.date = None, None, None  # Handle if no proposed grade or score exists
    
    # Extract grades from the routes for the histogram
    grades = [route.grade for route in routes]
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
    full_grade_frequencies = {grade: grade_frequencies.get(grade, 0) for grade in french_grades}
    #img = generate_histogram(grades)
    return render_template('users/user_page.html', user=user, routes=routes, sort_by=sort_by, full_grade_frequencies=full_grade_frequencies, nreps=nreps)





#####################################################################
@users.route('/update_username/<int:user_id>', methods=['POST'])
@login_required
def update_username(user_id):
    if current_user.id != user_id:
        flash('You are not authorized to edit this profile.', 'danger')
        return {'status': 'error', 'message': 'You are not authorized to edit this profile.'}, 403
    
    new_username = request.form.get('new_username')
    if new_username:
        current_user.username = new_username
        db.session.commit()
        return {'status': 'success', 'message': 'Username updated successfully!'}, 200
    else:
        return {'status': 'error', 'message': 'New username cannot be empty.'}, 400

    


@users.route('/update_password/<int:user_id>', methods=['POST'])
@login_required
def update_password(user_id):
    if current_user.id != user_id:
        return {'status': 'error', 'message': 'You are not authorized to edit this profile.'}, 403

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Verifica della password corrente
    if  current_user.password != current_password:
        return {'status': 'error', 'message': 'Current password is incorrect.'}, 400

    # Verifica che la nuova password non sia vuota
    if not new_password:
        return {'status': 'error', 'message': 'New password cannot be empty.'}, 400

    # Aggiornamento della password
    current_user.password = new_password
    db.session.commit()

    return {'status': 'success', 'message': 'Password updated successfully!'}, 200


@users.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):


    if current_user.id != user_id:
            flash('You are not authorized to edit this profile.', 'danger')
            return redirect(url_for('users.user_page', user_id=user_id))
        
    new_username = request.form.get('new_username')
    if new_username:
        current_user.username = new_username
        db.session.commit()
        flash('Username updated successfully!', 'success')
    else:
        flash('Username cannot be empty.', 'danger')


    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Verifica della password corrente
    if  current_user.password != current_password:
        flash('Wrong password.', 'danger')

    # Verifica che la nuova password non sia vuota
    elif not new_password:
        flash('New password is empty.', 'danger')

    # Aggiornamento della password
    else:
        current_user.password = new_password
        db.session.commit()
        flash('Password updated successfully!', 'success')

    return render_template('users/edit_profile.html', user_id=user_id)
#####################################################################







# USERS LIST
@users.route('/users')
def users_list():
    #users = User.query.all()  # Fetch all users from the database
    sort_order = request.args.get('sort', 'default')

    # Define conversion: "Project" → -1, else keep the grade
    grade_value = case(
        (Route.grade == 'Project', -1),
        else_=Route.grade
    )
    
    # Query for each user, counting repetitions and finding max grade
    users_with_stats = db.session.query(
    User.id, User.username,
    func.count(user_route.c.route_id).label('repetitions'),
    func.max(grade_value).label('max_grade')
    ).outerjoin(user_route, User.id == user_route.c.user_id) \
    .outerjoin(Route, Route.id == user_route.c.route_id) \
    .group_by(User.id)
    
    if sort_order == 'alph':
        users_with_stats = users_with_stats.order_by(func.lower(User.username))
    elif sort_order == 'nreps':    
        users_with_stats = users_with_stats.order_by(func.count(user_route.c.route_id).desc())
    elif sort_order == 'maxgrade':    
        users_with_stats = users_with_stats.order_by(func.max(grade_value).desc())
    else:
        users_with_stats = users_with_stats.order_by(User.id)

    users = users_with_stats.all()
    n_users = len(users)

    # Check if the user is logged in
    if current_user.is_authenticated:
        current_username = current_user.username
    else:
        current_username = None  # No logged-in user
    return render_template('users/users_list.html', users=users, current_username=current_username, sort_order=sort_order, n_users=n_users)








