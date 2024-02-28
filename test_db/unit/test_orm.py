import pytest
from games.domainmodel.model import Publisher, Genre, Game, User, Review, Wishlist
from test_db.conftest import empty_session
from sqlalchemy.exc import IntegrityError

def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "Watermelon123"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (user_name, password) VALUES (:user_name, :password)',
                          {'user_name': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where user_name = :user_name',
                                {'user_name': new_name}).fetchone()
    return row[0]