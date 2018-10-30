"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    # check if the user is logged in and pass to template
    is_logged_in = session.get('user_id')

    return render_template('homepage.html', isLoggedIn = is_logged_in)


@app.route('/users')
def show_users():
    """Show all the users in the system"""
    all_users = db.session.query(User).all() # list of User objects

    return render_template('users.html', users = all_users)


@app.route('/users/<int:user_id>')
def show_user_detail(user_id):
    """Show the details for one user"""
    user = db.session.query(User).filter(User.user_id == user_id).first()

    # To Do: order the movies in alphabetical order

    return render_template('user-detail.html', user=user)


@app.route('/movies')
def show_movies():
    """Show all the movies in the system"""

    all_movies = db.session.query(Movie).order_by('title').all() # list of Movie objects

    return render_template('movies.html', movies = all_movies)


@app.route('/register')
def show_register_form():
    """Display the registration form"""

    return render_template('registration.html')


@app.route('/create-user', methods=["POST"])
def create_user():
    """Create user in the database 
    (check email to see if they already exist in the system)
    """

    user_email = request.form.get('email')
    user_pwd = request.form.get('password')
    user_age = int(request.form.get('age'))
    user_zipcode = request.form.get('zipcode')
    
    user_query = db.session.query(User).filter(User.email == user_email).all()
    
    if not user_query: # if that list is empty, the email doesn't exist in the database
        new_user = User(email=user_email, password=user_pwd, age=user_age, zipcode=user_zipcode)
        db.session.add(new_user)
        db.session.commit()
        print("user added")
        flash('User registered!')
    else:
        flash('User email already exists')

    return redirect('/') # redirect to the registration form for now


@app.route('/login', methods=['GET'])
def show_login_form():
    """ Display the login form """
    return render_template('login.html')


@app.route('/login-user', methods=['POST'])
def login_user():
    """Take the user email and password and log them in if those match the database"""

    user_email = request.form.get('email')
    user_pwd = request.form.get('password')

    user = db.session.query(User).filter(User.email == user_email).first()

    if user and user_pwd == user.password:
        session['user_id'] = user.user_id
        flash("You've been logged in!")
        return redirect('/users/' + str(user.user_id))
    else:
        flash("Password or Email doesn't match")
        return redirect('/login')


@app.route('/logout', methods=['GET'])
def logout_user():
    """Log out the user by removing the user_id from the session"""

    if session.get('user_id'):
        del session['user_id']
        flash("You've been logged out!")
        return redirect('/')
    else: 
        flash("Log Out unsuccessful")
        return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
