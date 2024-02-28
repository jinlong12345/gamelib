import math
from flask import Blueprint, request, url_for, session, redirect

import games.adapters.repository as repo
from games.utilities import services

utilities_blueprint = Blueprint('utilities_bp', __name__)

def get_featured_genres():
    # Use the repository and session manager to get genres sorted by popularity
    genres = services.get_genres_sorted_by_popularity(repo.repo_instance)

    # Add link to each genre to use in view
    for g in genres:
        g['hyperlink'] = url_for('genres_bp.genre', genre_name=g['genre_name'])

    return genres

# Pagination information, used for browse, genres, and search
# This function uses the request object to retrieve query information about the current page
# and sets the max number of games per page as a default of 15 so that this is standardized across the app
def pagination(total_games: int, num_games_per_page=15):
    return services.get_pagination_info(total_games, num_games_per_page)

@utilities_blueprint.route('/toggle-theme',  methods=['POST'])
def toggle_theme():
    # Set a cookie to remember if on dark mode or light mode so it can be used throughout the app
    current_theme = session.get('theme')

    # Toggle the theme
    if current_theme == 'dark':
        session['theme'] = 'light'
    else:
        session['theme'] = 'dark'

    # Redirect user to the current page once the cookie is set
    return redirect(request.args.get('current_page'))