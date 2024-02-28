from flask import Blueprint, render_template, current_app
import games.adapters.repository as repo

import games.utilities.utilities as utilities
import games.home.services as services

home_blueprint = Blueprint('home_bp', __name__)

@home_blueprint.route('/', methods=['GET'])
def home():

    # Call get_featured_genres and pass the repo_instance
    featured_genres = utilities.get_featured_genres()
    featured_games = services.get_most_recent_games(repo.repo_instance)

    return render_template('home/home.html', featured_genres=featured_genres, featured_games=featured_games)
