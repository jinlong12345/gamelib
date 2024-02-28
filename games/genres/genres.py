from flask import Blueprint, render_template, url_for, request, redirect
import games.genres.services as services

import games.utilities.utilities as utilities

import games.adapters.repository as repo

# Configure Blueprint
genres_blueprint = Blueprint('genres_bp', __name__)

@genres_blueprint.route('/genres', methods=['GET'])
def browse_genres():
    # Retrieve genres to display
    all_genres = services.get_genres(repo.repo_instance)
    featured_genres = utilities.get_featured_genres()

    # Add urls to each genre dict to use in view layer
    for g in all_genres:
        g['hyperlink'] = url_for('genres_bp.genre', genre_name=g['genre_name'])

    return render_template('genres/genres.html',
                           # Custom page title
                           title=f'Browse genres | CS235 Game Library',
                           # Page heading
                           heading='Browse All Genres',
                           all_genres=all_genres,
                           featured_genres=featured_genres)

@genres_blueprint.route('/genres/<string:genre_name>', methods=['GET'])
def genre(genre_name: str):
    try:
        current_genre = services.get_genre(genre_name, repo.repo_instance)
    except services.NonExistentGenreException:
        # If invalid, redirect the user to all genres page
        return redirect(url_for('genres_bp.browse_genres'))

    featured_genres = utilities.get_featured_genres()
    num_games = services.get_number_of_games_for_genre(genre_name, repo.repo_instance)

    pagination_object = services.get_paginated_genre_games(genre_name, repo.repo_instance)

    # Add a link to each game dict for view layer
    for game in pagination_object['games']:
        game['hyperlink'] = url_for('games_bp.game', game_id=game['game_id'])

    return render_template(
        'browse/games.html',
        # Custom page title
        title=f'Browse {current_genre["genre_name"]} games | CS235 Game Library',
        # Page heading
        heading=f'Browse {current_genre["genre_name"]}  Games',
        games=pagination_object['games'],
        page_url=url_for('genres_bp.genre', genre_name=genre_name),
        current_page=pagination_object['page_number'],
        num_games=num_games,
        featured_genres=featured_genres,
        num_pages=pagination_object['num_pages'],
    )
