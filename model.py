"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True) # should we make this unique?
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    #db.String and db.Integer are imported from SQLAlchemy

    # ratings = db.relationship('Rating') # user can have multiple ratings

    def similarity(self, other):
        """Given 2 users, return the pearson correlation for the 2 users

        paired_ratings = [ (selfscore1, otherscore1), (selfscore2, otherscore2) ... ]
        """

        paired_ratings = []
        self_ratings = {} # dictionary of self's ratings {movie_id: score, ...}

        for rating in self.ratings:
            self_ratings[rating.movie_id] = rating.score

        for rating in other.ratings:
            if self_ratings.get(rating.movie_id):
                pair = (self_ratings[rating.movie_id], rating.score)
                paired_ratings.append(pair)

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0


    def predict_rating(self, movie):
        """Predict what the user will rate a given movie
        Returns a predicted score
        """

        # get all the ratings for this movie
        other_ratings = movie.ratings

        # list of tuples with the similarity of that user with other user and the other user
        # [ (similarity1, other_user1), (similarity2, other_user2) ... ]
        similarities = []

        for rating in other_ratings:
            similarity_pair = (self.similarity(rating.user), rating.score)
            similarities.append(similarity_pair)

        # sorted_users = sorted(similarities, reverse=True)
        similarities.sort(reverse=True)

        sim, score = similarities[0] # tuple (similarity score, user_id)

        predicted_score = score * sim
        return predicted_score


    def __repr__(self):
        """Provide helpful representation when printed"""
        return "<User user_id = {}, email={}>".format(self.user_id, self.email)


# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """All the movies in the ratings website"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imdb_url = db.Column(db.String(200), nullable=False)

    # ratings = db.relationship('Rating') # movie can have multiple ratings

    def __repr__(self):
        """Provide helpful representation when printed"""
        return """<Movie movie_id={} title={}>
        """.format(self.movie_id, self.title)


class Rating(db.Model):
    """All the ratings for the ratings website"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False) #foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) #foreign key
    score = db.Column(db.Integer, nullable=False)

    # define relationships between Rating <> User, Rating <> Movie
    # movie = db.relationship('Movie') # rating has 1 movie
    # user = db.relationship('User') # rating has 1 user
    # user = db.relationship("User", backref='ratings')
    # movie = db.relationship('Movie', backref='ratings')
    movie = db.relationship('Movie', backref=db.backref('ratings', order_by=movie_id))
    user = db.relationship('User', backref=db.backref('ratings', order_by=movie_id))

    # documentation on backref: https://docs.sqlalchemy.org/en/latest/orm/backref.html
    # order_by parameter in the backref function determines what to sort the ratings by

    def __repr__(self):
        """Provide helpful representation when printed"""
        return """<Rating rating_id={} movie_id={} user_id={} score={}>
        """.format(self.rating_id, self.movie_id, self.user_id, self.score)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

def get_paired_ratings(user1, user2):
    """Given 2 users, return a list of tuples of ratings of movies 
    that they have both rated

    paired_ratings = [ (user1score1, user2score1), (user1score2, user2score2) ... ]

    outputs the pearson correlation for the two pairs
    """
    paired_ratings = []
    user1_ratings = {} # dictionary of user1's ratings {movie_id: score, ...}

    for rating in user1.ratings:
        user1_ratings[rating.movie_id] = rating.score

    for rating in user2.ratings:
        if user1_ratings.get(rating.movie_id):
            pair = (user1_ratings[rating.movie_id], rating.score)
            paired_ratings.append(pair)

    if paired_ratings:
        return correlation.pearson(paired_ratings)
    else:
        return 0.0

    # return paired_ratings


def predict_movie_rating(user, movie):
    """Predict what the user will rate a given movie
    Returns a predicted score
    """

    # get all the other users who have rated the movie
    other_users = [rating.user for rating in movie.ratings]
    other_ratings = movie.ratings

    # list of tuples with the similarity of that user with other user and the other user
    # [ (similarity1, other_user1), (similarity2, other_user2) ... ]
    similarities = []

    for other in other_users:
        similarity_pair = (user.similarity(other), other)
        similarities.append(similarity_pair)  

    sorted_users = sorted(similarities, reverse=True)

    sim, most_similar_user = sorted_users[0] # tuple (similarity score, <User>)

    for rating in other_ratings:
        if rating.user_id == most_similar_user.user_id:
            predicted_score = rating.score * sim
            return predicted_score


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
