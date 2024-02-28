from games.browse.services import games_to_dict
from games.domainmodel.model import Genre
from games.adapters.repository import AbstractRepository

from typing import Iterable
import games.utilities.utilities as utilities


class NonExistentGenreException(Exception):
    pass


def get_genre(genre_name: str, repo: AbstractRepository):
    # Check that the genre exists
    genre = repo.get_genre(genre_name)

    if genre is None:
        raise NonExistentGenreException

    return genre_to_dict(genre)


def get_genres(repo: AbstractRepository):
    genres = repo.get_genres()

    # Convert genres to dict form
    genres_as_dict = genres_to_dict(genres)

    return genres_as_dict


def get_games_for_genre(genre_name: str, repo: AbstractRepository):
    games = repo.get_games_for_genre(genre_name)

    # Convert games to dict form
    games_as_dict = games_to_dict(games)

    return games_as_dict


def get_paginated_genre_games(genre_name: str, repo: AbstractRepository):
    # Get all games associated with that genre
    games = get_games_for_genre(genre_name, repo)

    pagination_object = utilities.pagination(len(games))
    # Slice the games so that you return only the required games for this page
    # The offset will be the num_games_per_page * page number -1 to 0-index
    starting_idx = pagination_object['num_games_per_page'] * (pagination_object['page_number'] - 1)

    # The limit (aka list length returned) here is num_games_per_page
    ending_idx = starting_idx + pagination_object['num_games_per_page']

    return {'games': games[starting_idx:ending_idx], **pagination_object}


def get_number_of_games_for_genre(genre_name: str, repo: AbstractRepository):
    return repo.get_num_games_for_genre(genre_name)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def genre_to_dict(genre: Genre):
    genre_dict = {
        'genre_name': genre.genre_name,
    }

    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]
