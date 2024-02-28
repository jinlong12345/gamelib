import math

from flask import request

from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Genre, Game


def get_genres_sorted_by_popularity(repo: AbstractRepository) -> dict[str, int]:
    # Get all genres and games
    genres = repo.get_genres()
    games = repo.get_games()

    # Make a dict that looks like: [{'genre_name': number_of_instances}]
    genre_names = [genre.genre_name for genre in genres]
    genreDict = dict.fromkeys(genre_names, 0)

    # Count the number of games with that genre
    for game in games:
        for genre in game.genres:
            genreDict[genre.genre_name] += 1

    # Turn dict into list to sort it
    genre_list = [[genre_name, genreDict[genre_name]] for genre_name in genreDict.keys()]

    # Sort the list by most popular genre
    genre_list.sort(key=lambda x: x[1], reverse=True)

    return genre_tuples_to_dict(genre_list)

def get_pagination_info(total_games: int, num_games_per_page=15):
    # Total number of pages
    num_pages = math.ceil(total_games / num_games_per_page)

    # Get page number from query string
    page_number_query = request.args.get('page')

    # If invalid page number or user just visits /games, show the first page
    if page_number_query is None or not page_number_query.isnumeric():
        page_number = 1
    else:
        page_number = int(page_number_query)

        if page_number < 1:
            page_number = 1

    # Return pagination information which will be used by the view
    return {'num_games_per_page': num_games_per_page, 'num_pages': num_pages, 'page_number': page_number}


# ============================================
# Functions to convert model entities to dicts
# ============================================
def genre_tuple_to_dict(genre):
    genre_dict = {
        'genre_name' : genre[0]
    }

    return genre_dict

def genre_tuples_to_dict(genres):
    return [genre_tuple_to_dict(genre) for genre in genres]
