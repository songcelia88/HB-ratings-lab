"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Rating, Movie, connect_to_db,db

from server import app
from datetime import datetime # need this to convert our dates to datetime format


def load_users(filename):
    """Load users from u.user into database."""

    print("Loading Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open(filename):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies(filename):
    """Load movies from u.item into database."""

    print("Loading Movies")

    Movie.query.delete()

    with open(filename) as file:
        for line in file:
            line = line.strip()
            info = line.split("|")
            movie_id = info[0]
            title = info[1][:-7] # strip the last 7 characters in the title, i.e. take out year
            if info[2]:
                released_at = datetime.strptime(info[2], "%d-%b-%Y") #convert datetime format
            else:
                released_at = None;
            # print("movie: {}, date: {}".format(title, date))
            imdb_url = info[4]

            movie = Movie(movie_id=movie_id,title=title,released_at=released_at, imdb_url=imdb_url)

            db.session.add(movie)

    db.session.commit()



def load_ratings(filename):
    """Load ratings from u.data into database."""
    print("Loading Ratings")

    Rating.query.delete()

    with open(filename) as file:
        for line in file:
            line = line.strip()
            user_id, movie_id, score, timestamp = line.split("\t") # split by tab
            # print("user_id: {} movie_id: {} score: {}".format(user_id,movie_id,score))
            rating = Rating(movie_id=movie_id, user_id=user_id,score=score)

            db.session.add(rating)

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users("seed_data/u.user")
    load_movies("seed_data/u.item")
    load_ratings("seed_data/u.data")
    set_val_user_id()
