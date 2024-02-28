from datetime import datetime

from games.authentication.services import UnknownUserException
from games.domainmodel.model import Game, make_review, Review, delete_review
from games.adapters.repository import AbstractRepository

from typing import Iterable, List


class NonExistentGameException(Exception):
    pass


def get_number_of_games(repo: AbstractRepository):
    return repo.get_number_of_games()


def get_games(repo: AbstractRepository):
    # Gets game from repo
    games = repo.get_games()

    # Alphabetically sort games
    sort_games_alphabetically(games)

    #Creates list to store game_dicts
    game_dicts = []
    for game in games:
        game_dicts.append(game_to_dict(game))
    return game_dicts

def sort_games_alphabetically(games: List[Game]) -> List[Game]:
    games.sort(key=lambda g: g.title)

def get_games_for_page(page_number: int, num_games_per_page: int, repo: AbstractRepository):
    # Get all games first
    games = get_games(repo)
    # The offset will be the num_games_per_page * page number -1 to 0-index
    starting_idx = num_games_per_page * (page_number - 1)
    # The limit (aka list length returned) here is num_games_per_page
    ending_idx = starting_idx + num_games_per_page

    return games[starting_idx:ending_idx]


def get_game(game_id: int, repo: AbstractRepository):
    # Check the game exists
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    return game_to_dict(game)

def add_review(game_id: int, review_text: str, rating: int, username: str, repo: AbstractRepository):
    # Check the game exists
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Check the user has not already reviewed the game before making the review
    if not check_has_user_reviewed_game(game_id, username, repo):
        # Valid user and game, add the review
        review = make_review(review_text, rating, user, game)

        # Update repository
        repo.add_review(review)

def discard_review(game_id: int, username: str, repo: AbstractRepository):
    # Check the game exists
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    # Check it's a valid user
    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Now you've verified the game and user, retrieve the review object
    review = repo.get_user_review_for_game(user, game)

    # Remove the review in the model (removes the review from the user and the game objects)
    delete_review(review)

    # Update repository
    repo.remove_review(review)

def get_reviews_for_game(game_id: int, repo: AbstractRepository):
    # Check game exists
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    # Automatically sort by date posted, descending (from most to least recent)
    game.reviews.sort(key=lambda r: datetime.strptime(r.time_posted, "%b %d, %Y at %H:%M:%S"), reverse=True)

    return reviews_to_dict(game.reviews)

def check_has_user_reviewed_game(game_id: int, username: str, repo: AbstractRepository):
    game = repo.get_game(game_id)

    if any(review.user.username == username for review in game.reviews):
        return True

    return False

# Calculates the average rating for a game. Returns None if no reviews have been submitted
def calculate_average_rating_for_game(game_id: int, repo: AbstractRepository):
    game = repo.get_game(game_id)

    average = None
    counter = 0
    total_rating = 0

    for review in game.reviews:
        counter = counter + 1
        total_rating = total_rating + review.rating

    if counter > 0:
        average = round(total_rating/counter)

    return average

# Helper method to check that a game is in the user's favourites already
def check_game_in_favourites(game_id: int, username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    game = repo.get_game(game_id)

    if game is None:
        raise NonExistentGameException

    # Don't need to raise an error if the user doesn't exist, just leave them on the game description page
    if user is not None:
        return repo.is_game_in_favourites(user, game)

    return False

# ============================================
# Functions to convert model entities to dicts
# ============================================

def game_to_dict(game: Game):
    game_dict = {
        'game_id': game.game_id,
        'title': game.title,
        'price': game.price,
        'release_date': game.release_date,
        'description': game.description,
        'image_url': game.image_url,
        'publisher': game.publisher.publisher_name,
        #'recommendations': game.recommendations,
        #"website": game.website,
        #"developer": game.developer,
        # Create a list of genre names as the genres property
        'genres': [genre.genre_name for genre in game.genres],
        #"windows": game.windows,
        #"mac": game.mac,
        #"linux": game.linux,
        #"movie": game.movie,
    }

    return game_dict


def games_to_dict(games: Iterable[Game]):
    return [game_to_dict(game) for game in games]

def review_to_dict(review: Review):
    review_dict = {
        'username': review.user.username,
        'game_id': review.game.game_id,
        'game_title': review.game.title,
        'comment': review.comment,
        'rating': review.rating,
        'time_posted': review.time_posted
    }

    return review_dict
def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]