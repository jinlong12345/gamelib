from typing import Iterable, List

from games.adapters.repository import AbstractRepository
from games.browse.services import games_to_dict, game_to_dict

import games.genres.services as genreServices
from games.domainmodel.model import Publisher, Game


class NonExistentSearchKeyException(Exception):
    pass

def get_publishers(repo: AbstractRepository):
    publishers = repo.get_publishers()

    # Convert publishers to dict form
    publishers_as_dict = publishers_to_dict(publishers)

    return publishers_as_dict

# Retrieve a game based off a publisher name. If no games exist, return an empty list
def get_games_for_publisher(publisher_name: str, repo: AbstractRepository):
    games = repo.get_games_for_publisher(publisher_name)

    # Convert games to dict form
    games_as_dict = games_to_dict(games)

    return games_as_dict

# Retrieve a game based off a title. If no game exists, return None
def get_game_from_title(title: str, repo: AbstractRepository):
    game = repo.get_game_from_title(title)

    if game:
        game_as_dict = game_to_dict(game)

        return game_as_dict
    else:
        return None

def get_games_from_search_query(request, repo: AbstractRepository):
    search_result = list()
    term = None

    # Default variables to pass on to the view layer
    for arg in request.args:
        # If the user has typed in an invalid search key (i.e. from the URL), then throw an error & redirect to main search page at search layer
        if arg not in ['term', 'price_max', 'publisher', 'genres']:
            raise NonExistentSearchKeyException("Invalid search key. Please try again.")

    # Retrieve the search key
    if (request.args.get("term")):
        term = request.args.get("term").strip()

    if term:
        # Find all games associated with this term
        # First search by publisher and genre
        search_result = get_games_for_publisher(term, repo) + genreServices.get_games_for_genre(term, repo)

        # See if a game with the title exists
        game = get_game_from_title(term, repo)

        # If game isn't None, then append result to search_results
        if game:
            search_result.append(game)

    # Filtering
    if (request.args.get("publisher")):
        # Filter games by publisher
        search_result = filter_games_by_publisher(request.args.get('publisher'), search_result)

    if (request.args.get("price_max")):
        # Filter games by price
        search_result = filter_games_by_price(request.args.get('price_max'), search_result)

    # Use getlist as there can be multiple genres selected
    if (request.args.getlist("genres")):
        # Filter games by selected genres
        search_result = filter_games_by_genre(request.args.getlist('genres'), search_result)

    return search_result

# Filter games by publisher if the user has chosen to filter by publisher
def filter_games_by_publisher(publisher_name: str, games):
    filtered_result = list()

    def has_publisher(game):
        return game['publisher'].lower() == publisher_name.lower()

    if len(games):
        filtered_result = list(filter(has_publisher, games))

    return filtered_result

# Filter games by price if the user has chosen to filter by price
def filter_games_by_price(price: str, games):
    filtered_result = list()

    try:
        filter_price = float(price)

        if filter_price < 0:
            raise NonExistentSearchKeyException(f"{price} is not a valid price. Please input a number greater than 0.")
        def price_within_range(game):
            return game['price'] <= filter_price

        if len(games):
            filtered_result = list(filter(price_within_range, games))

    except:
        raise NonExistentSearchKeyException(f"{price} is not a valid price. Please input a number greater than 0.")

    return filtered_result

# Filter games by genre if the user has chosen to filter by genre
def filter_games_by_genre(genres: List[str], games):
    filtered_result = list()

    def matches_genre(game):
        for genre in genres:
            if genre.lower() in [g.lower() for g in game['genres']]:
                return True

        return False

    if len(games):
        filtered_result = list(filter(matches_genre, games))

    return filtered_result

# ============================================
# Functions to convert model entities to dicts
# ============================================

def publisher_to_dict(publisher: Publisher):
    publisher_dict = {
        'publisher_name': publisher.publisher_name
    }

    return publisher_dict

def publishers_to_dict(publishers: Iterable[Publisher]):
    return [publisher_to_dict(publisher) for publisher in publishers]