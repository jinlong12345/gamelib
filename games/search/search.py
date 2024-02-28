from flask import Blueprint, render_template, request, url_for, redirect

import games.adapters.repository as repo
import games.search.services as services
import games.utilities.utilities as utilities

# Configure Blueprint
search_blueprint = Blueprint('search_bp', __name__)

@search_blueprint.route('/search', methods=['GET'])
def search():
    result = list()
    error_message = None
    term = request.args.get('term')

    try:
        # Pass the request object to controller to retrieve search results
        result = services.get_games_from_search_query(request, repo.repo_instance)

        if term:
            if not len(term.strip()):
                error_message="Search term should not be blank."

    except services.NonExistentSearchKeyException as err:
        # If the search key doesn't exist, generate an error message to display
        error_message=err

    featured_genres = utilities.get_featured_genres()
    publishers = services.get_publishers(repo.repo_instance)

    return render_template('search/search.html',
                           featured_genres=featured_genres,
                           publishers=publishers,
                           results=result,
                           term=term,
                           error_message=error_message,
                           title=f'Search games | CS235 Game Library',
                           )
