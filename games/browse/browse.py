from flask import Blueprint, render_template, session, redirect, url_for, request
import games.browse.services as services

from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

import games.utilities.utilities as utilities
import games.adapters.repository as repo
from games.authentication.authentication import login_required
from games.authentication.services import UnknownUserException

# Configure Blueprint
browse_blueprint = Blueprint('games_bp', __name__)

@browse_blueprint.route('/games/', methods=['GET'])
def browse_games():
    num_games = services.get_number_of_games(repo.repo_instance)

    # Get pagination information
    pagination_object = utilities.pagination(num_games)

    # If the user tries to visit a page that's too high, redirect them to the last page
    if pagination_object['page_number'] > pagination_object['num_pages']:
        return redirect(f"/games?page={pagination_object['num_pages']}")

    games_to_display = services.get_games_for_page(pagination_object['page_number'], pagination_object['num_games_per_page'], repo.repo_instance)
    featured_genres = utilities.get_featured_genres()

    return render_template(
        'browse/games.html',
        # Custom page title
        title=f'Browse games | CS235 Game Library',
        # Page heading
        heading='Browse Games',
        games=games_to_display,
        page_url=url_for('games_bp.browse_games'),
        current_page=pagination_object['page_number'],
        num_games=num_games,
        featured_genres=featured_genres,
        num_pages=pagination_object['num_pages'],
    )

@browse_blueprint.route('/games/<int:game_id>', methods=['GET'])
def game(game_id):
    # Create form. The form maintains state, so when this method is called with a GET request it populates the form
    # with a game_id, when review_game() is subsequently called with a POST request, the game id remains in the form.
    form = ReviewForm()

    # If the user has already left a review, give them the option to delete it. Set this as None first
    delete_review_url = None
    is_game_in_favourites = False

    try:
        current_game = services.get_game(game_id, repo.repo_instance)
        reviews = services.get_reviews_for_game(game_id, repo.repo_instance)
        average_rating = services.calculate_average_rating_for_game(game_id, repo.repo_instance)

        # If the user has signed in, check if they've already reviewed and/or favourited the game
        if "username" in session:
            if services.check_has_user_reviewed_game(game_id, session["username"], repo.repo_instance):
                delete_review_url = url_for("games_bp.delete_review", game=game_id)

            is_game_in_favourites = services.check_game_in_favourites(game_id, session["username"], repo.repo_instance)

        # If valid game, then store game id in the form.
        form.game_id.data = game_id

    except services.NonExistentGameException:
        # If invalid, redirect the user to all games page
        return redirect(url_for('games_bp.browse_games'))


    featured_genres = utilities.get_featured_genres()
    # Use Jinja to customize a predefined html page rendering the layout for showing a single game.
    return render_template('browse/gameDescription.html',
                           game=current_game,
                           is_game_in_favourites=is_game_in_favourites,
                           featured_genres=featured_genres,
                           average_rating=average_rating,
                           form=form,
                           delete_review_url=delete_review_url,
                           reviews=reviews,
                           handler_url=url_for('games_bp.review_game'),
                           title=f'About {current_game.get("title")} | CS235 Game Library',)

@browse_blueprint.route("/review", methods=["POST"])
@login_required
def review_game():
    # Create form. The form maintains state, so when this method is called with a GET request it populates the form
    # with a game_id, when review_game() is subsequently called with a POST request, the game id remains in the form.
    form = ReviewForm()

    # Obtain username of current user.
    username = session["username"]

    if form.validate_on_submit():
        # Successful POST, ie the review passed data validation.
        # Extract the game id, representing the reviewed game, from the form.
        game_id = int(form.game_id.data)

        try:
            # Use services layer to store the review
            services.add_review(game_id, form.comment.data, form.rating.data, username, repo.repo_instance)

        # If the user was trying to submit a POST request for an invalid game, then redirect them to the games page
        except services.NonExistentGameException:
            return redirect(url_for('games_bp.browse_games'))

        # If the user does not exist, redirect them to login page
        except UnknownUserException:
            return redirect(url_for('authentication_bp.login'))

    # Request is a HTTP POST where validation has failed.
    # Extract game id of game being reviewed from form
    game_id = int(form.game_id.data)

    # For all POST requests (successful & unsuccessful), redirect the user to the game description page. The user
    # will either see the form again with the rendered errors or else a list of reviews with their new review.
    return redirect(url_for("games_bp.game", game_id=game_id))

@browse_blueprint.route("/delete-review", methods=["GET"])
@login_required
def delete_review():
    try:
        # Get the game to delete the review for
        game_id = int(request.args.get('game'))

        services.get_game(game_id, repo.repo_instance)

        # If the game exists, then delete the review
        services.discard_review(game_id, session["username"], repo.repo_instance)

        # After successfully deleting the review, redirect the user to the game description page.
        return redirect(url_for("games_bp.game", game_id=game_id))

    # In the case where a game does not exist or an invalid game id is part of the param, then redirect user to browse
    except:
        # If the game to delete does not exist, redirect the user to all games page
        return redirect(url_for('games_bp.browse_games'))

class ReviewForm(FlaskForm):
    # TO DO: Consider making this a radio for better UX
    # rating = RadioField('Rating(0-5)', [DataRequired(), NumberRange(min=0, max=5, message="Please submit a rating between 0 and 5.")], choices=[(0,'0'), (1,'1'), (2,'2'), (3, '3'), (4, '4'), (5, '5')])
    rating = IntegerField("Rating (0-5)", [DataRequired(), NumberRange(min=0, max=5, message="Please submit a rating between 0 and 5.")])
    comment = TextAreaField("Comment", [DataRequired(), Length(min=3, message="Review comments must be longer than 3 characters")])
    username = HiddenField("username")
    game_id = HiddenField("game_id")
    submit = SubmitField("Post review")