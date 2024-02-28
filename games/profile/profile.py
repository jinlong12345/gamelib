from flask import Blueprint, render_template, url_for, request, redirect, session
import games.adapters.repository as repo
from games.authentication.authentication import login_required
import games.utilities.utilities as utilities
import games.profile.services as services
from games.authentication.services import UnknownUserException

# Configure Blueprint
profile_blueprint = Blueprint('profile_bp', __name__)


@profile_blueprint.route("/profile", methods=["GET"])
@login_required
def user_profile():
    featured_genres = utilities.get_featured_genres()
    current_user = session["username"]
    try:
        user_reviews = services.get_user_reviews(current_user, repo.repo_instance)
        user_favourites = services.get_user_favourites(current_user, repo.repo_instance)
        most_recent_review = services.get_most_recent_review(current_user, repo.repo_instance)
        most_recent_favourite = services.get_most_recent_favourite(current_user, repo.repo_instance)

    # If for some reason the username is invalid in the session, then redirect to login
    except UnknownUserException:
        return redirect(url_for("authentication_bp.login"))

    return render_template("profile/profile.html",
                           title=f"User Profile | CS235 Game Library" ,
                           featured_genres=featured_genres,
                           reviews=user_reviews,
                           favourites=user_favourites,
                           most_recent_review=most_recent_review,
                           most_recent_favourite=most_recent_favourite)

@profile_blueprint.route("/favourites", methods=["GET"])
@login_required
def see_favourites():
    try:
        featured_genres = utilities.get_featured_genres()
        favourite_games = services.get_user_favourites(session["username"], repo.repo_instance)

    # If for some reason the username is invalid in the session, then redirect to login
    except UnknownUserException:
        return redirect(url_for("authentication_bp.login"))

    return render_template(
        'profile/favourites.html',
        title="Favourite Games | CS235 Game Library",
        favourite_games=favourite_games,
        featured_genres=featured_genres,
    )



@profile_blueprint.route("/favourite", methods=["GET"])
@login_required
def favourite_game():
    try:
        game_id = int(request.args.get('game_id'))

        # If the game exists, then add it to the user's favourites
        services.add_game_to_favourites(game_id, session["username"], repo.repo_instance)

        # After successfully favouriting the game, redirect the user to the game description page.
        return redirect(url_for("games_bp.game", game_id=game_id))

    # In the case where a game does not exist or an invalid game id is part of the param, then redirect user to all games
    except:
        return redirect(url_for('games_bp.browse_games'))


@profile_blueprint.route("/unfavourite", methods=["GET"])
@login_required
def remove_favourite():
    def redirect_url(game_id: int):
        return request.args.get('next') or \
            request.referrer or \
            url_for('games_bp.game', game_id=game_id)

    try:
        game_id = int(request.args.get('game_id'))

        # If the game exists, then try to remove it from the user's favourites
        services.remove_game_from_favourites(game_id, session["username"], repo.repo_instance)

        # After removing the game, redirect the user back to where they came from (could be the favourites list), or else back to the game page
        return redirect(redirect_url(game_id))

    # In the case where a game does not exist or an invalid game id is part of the param, then redirect user to all games
    except:
        return redirect(url_for('games_bp.browse_games'))

