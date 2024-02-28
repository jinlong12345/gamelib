from werkzeug.security import generate_password_hash, check_password_hash

from games.adapters.repository import AbstractRepository
from games.domainmodel.model import User


class NameNotUniqueException(Exception):
    pass

class UnknownUserException(Exception):
    pass

class AuthenticationException(Exception):
    pass

def add_user(username: str, password: str, repo: AbstractRepository):
    # Check the username is not taken
    user = repo.get_user(username)

    if user:
        raise NameNotUniqueException

    # Encrypt password
    password_hash = generate_password_hash(password)

    # Create and store new User with given username & encrypted password
    user = User(username, password_hash)
    repo.add_user(user)

def get_user(username: str, repo: AbstractRepository):
    user = repo.get_user(username)

    if user is None:
        raise UnknownUserException

    return user_to_dict(user)

def authenticate_user(username: str, password: str, repo: AbstractRepository):
    authenticated = False

    user = repo.get_user(username)
    if user is not None:
        authenticated = check_password_hash(user.password, password)
    if not authenticated:
        raise AuthenticationException

# ============================================
# Functions to convert model entities to dicts
# ============================================

def user_to_dict(user: User):
    user_dict = {
        'username': user.username,
        'password': user.password,
        'favourite_games': user.favourite_games
    }

    return user_dict
