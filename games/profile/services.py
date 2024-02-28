from datetime import datetime
from typing import List, Dict
from games.adapters.repository import AbstractRepository
from games.authentication.services import UnknownUserException
from games.browse.services import NonExistentGameException, games_to_dict, reviews_to_dict
from games.domainmodel.model import Review, User


def add_game_to_favourites(game_id: int, username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    # Check the game exists
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    if user is None:
        raise UnknownUserException

    repo.add_game_to_favourites(user, game)

def remove_game_from_favourites(game_id: int, username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    # Check the game exists
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    if user is None:
        raise UnknownUserException

    # This method checks if the game is in the favourites and removes it if it is
    repo.remove_game_from_favourites(user, game)

def get_user_favourites(username: str, repo: AbstractRepository):
    """ Retrieve the users favourite games"""

    user = repo.get_user(username)

    if user is None:
        raise UnknownUserException

    return repo.get_favourites(user)

def get_user_reviews(username: str, repo: AbstractRepository) -> List[Dict]:
    """ Retrieve the users reviews """

    user = repo.get_user(username)

    if user is None:
        raise UnknownUserException

    # Automatically sort by date posted, descending (from most to least recent)
    user.reviews.sort(key=lambda r: datetime.strptime(r.time_posted, "%b %d, %Y at %H:%M:%S"), reverse=True)

    return repo.get_reviews(user)

def get_most_recent_review(username: str, repo: AbstractRepository):
    # Get dictionaries
    review_dicts = get_user_reviews(username, repo)

    # If the user has no reviews, return None
    if len(review_dicts):
        # These should be sorted by date, so returning the first object in the list should return the most recent review
        return review_dicts[0]

    return None

def get_most_recent_favourite(username: str, repo: AbstractRepository):
    # Get favourites
    favourite_dicts = get_user_favourites(username, repo)

    # If the user has no favourites, return None
    if len(favourite_dicts):
        # These are appended to the end of the favourite_games list, so returning the last one should return the most
        # recent favourite
        return favourite_dicts[-1]

    return None



