import pytest

from flask import request

from games import create_app
from datetime import date

from games.authentication.services import AuthenticationException, UnknownUserException
from games.browse import services as games_services
from games.domainmodel.model import Game, User, Review
from games.genres import services as genres_services
from games.home import services as home_services
from games.search.services import NonExistentSearchKeyException
from games.utilities import services as utility_services
from games.search import services as search_services
from games.browse.services import NonExistentGameException
from games.authentication import services as auth_services
from games.profile import services as profile_services

# ------------------------- #
# TESTS FOR BROWSE/SERVICES #
# ------------------------- #
# Test user can retrieve a game object represented as dict from the repo
def test_can_get_game(in_memory_repo):
    game_id = 1

    game_as_dict = games_services.get_game(game_id, in_memory_repo)

    assert game_as_dict['game_id'] == game_id
    assert game_as_dict['release_date'] == date.fromisoformat('2007-11-12').strftime("%b %d, %Y")
    assert game_as_dict['title'] == 'Call of Duty® 4: Modern Warfare®'
    assert game_as_dict['price'] == 9.99


# Test retrieving non-existent game throws exception
def test_get_nonexistent_game(in_memory_repo):
    with pytest.raises(NonExistentGameException):
        games_services.get_game(900, in_memory_repo)


# Test user can retrieve all games
def test_can_get_all_games(in_memory_repo):
    games_as_dict = games_services.get_games(in_memory_repo)

    assert len(games_as_dict) == 10


# Test total games is calculated correctly
def test_can_get_number_of_games(in_memory_repo):
    assert games_services.get_number_of_games(in_memory_repo) == 10


# Test games can be sorted alphabetically correctly
def test_sort_games_alphabetically(in_memory_repo):
    games = in_memory_repo.get_games()
    # Check first and last games to make sure currently sorted by id, not alphabetically
    assert games[0].game_id == 1
    assert games[0].title == "Call of Duty® 4: Modern Warfare®"

    assert games[-1].game_id == 10
    assert games[-1].title == "Gladio and Glory"

    games_services.sort_games_alphabetically(games)
    for idx, game in enumerate(games):
        if idx != len(games) - 1:
            assert games[idx].title < games[idx + 1].title


# Test correct indices of games (sorted alphabetically by default) can be retrieved for pagination purposes
def test_can_get_games_for_page(in_memory_repo):
    # Retrieve alphabetically sorted games for testing purposes
    games = in_memory_repo.get_games()
    games_services.sort_games_alphabetically(games)

    test_game_limit = 2
    page_one = games_services.get_games_for_page(1, test_game_limit, in_memory_repo)
    page_three = games_services.get_games_for_page(3, test_game_limit, in_memory_repo)

    assert len(page_one) is test_game_limit

    # Test page 1 contains first 2 games from alphabetically sorted list
    for idx, game in enumerate(page_one):
        assert game.get('title') is games[idx].title

    # Test page 3 contains 4th and 5th indexed games from alphabetically sorted list
    for idx, game in enumerate(page_three):
        assert game.get('title') is games[idx + 4].title

# Test can add review
def test_add_review(in_memory_repo):
    test_game_id = 3

    assert len(games_services.get_reviews_for_game(test_game_id, in_memory_repo)) == 0

    games_services.add_review(test_game_id, "Nice game!", 5, "jess", in_memory_repo)

    assert len(games_services.get_reviews_for_game(test_game_id, in_memory_repo)) == 1

# Test error raised for invalid game
def test_add_review_invalid_game(in_memory_repo):
    with pytest.raises(NonExistentGameException):
        games_services.add_review(900, "This should fail", 0, "jess", in_memory_repo)


# Test error raised for unknown user
def test_add_review_unknown_username(in_memory_repo):
    with pytest.raises(UnknownUserException):
        games_services.add_review(1, "This should fail", 0, "Notauser", in_memory_repo)

# Test a second review for a game by a user does not get submitted
def test_does_not_add_duplicate_review(in_memory_repo):
    test_game_id = 3
    user = in_memory_repo.get_user("jess")

    assert len(games_services.get_reviews_for_game(test_game_id, in_memory_repo)) == 0

    games_services.add_review(test_game_id, "Nice game!", 5, user.username, in_memory_repo)

    assert len(games_services.get_reviews_for_game(test_game_id, in_memory_repo)) == 1
    assert len(user.reviews) == 3

    games_services.add_review(test_game_id, "Second review", 2, user.username, in_memory_repo)
    assert len(user.reviews) == 3

# Test the services layer can delete reviews
def test_discard_review(in_memory_repo):
    games_services.add_review(3, "Nice game!", 5, "jess", in_memory_repo)

    assert len(games_services.get_reviews_for_game(3, in_memory_repo)) == 1

    games_services.discard_review(3, "jess", in_memory_repo)

    assert len(games_services.get_reviews_for_game(3, in_memory_repo)) == 0

# Test reviews for a specified game can be retrieved by the services layer
def test_can_retrieve_reviews_as_dict_for_game(in_memory_repo):
    reviews = games_services.get_reviews_for_game(1, in_memory_repo)

    assert len(reviews) == 3
    assert reviews[0]['username'] == 'jess'
    assert reviews[0]['game_id'] == 1
    assert reviews[0]['comment'] == "Great game!"
    assert reviews[0]["rating"] == 5
    assert reviews[2]['username'] == 'david'
    assert reviews[2]['comment'] == "Was really hard"
    assert reviews[2]["rating"] == 3

    # Check reviews are sorted
    assert reviews[0]['time_posted'] >= reviews[1]["time_posted"]
    assert reviews[1]['time_posted'] >= reviews[2]["time_posted"]

# Test that the services layer correctly registers when a user has already reviewed a game
def test_user_has_reviewed_game(in_memory_repo):
    assert games_services.check_has_user_reviewed_game(3, "jess", in_memory_repo) is False

    games_services.add_review(3, "This was a great game!", 5, "jess", in_memory_repo)

    reviews = games_services.get_reviews_for_game(3, in_memory_repo)

    assert reviews[0]['username'] == 'jess'

    user_reviewed = games_services.check_has_user_reviewed_game(3, "jess", in_memory_repo)

    assert user_reviewed is True

# Test game's average rating is accurate
def test_calculate_average_rating(in_memory_repo):
    assert games_services.calculate_average_rating_for_game(1, in_memory_repo) == 3
    assert games_services.calculate_average_rating_for_game(2, in_memory_repo) == 3

# Test game services correctly picks up if a game is already in user favourites
def test_is_game_already_favourited(in_memory_repo):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(3)

    assert games_services.check_game_in_favourites(game.game_id, user.username, in_memory_repo) is False

    in_memory_repo.add_game_to_favourites(user, game)

    assert games_services.check_game_in_favourites(3, "jess", in_memory_repo) is True

# ------------------------- #
# TESTS FOR PROFILE/SERVICES #
# ------------------------- #

# Test game can be favourited
def test_add_game_to_favourites(in_memory_repo):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(3)

    assert in_memory_repo.is_game_in_favourites(user, game) is False

    profile_services.add_game_to_favourites(game.game_id, user.username, in_memory_repo)
    assert in_memory_repo.is_game_in_favourites(user, game) is True

# Test game can be removed from favourites
def test_remove_game_from_favourites(in_memory_repo):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(3)

    assert in_memory_repo.is_game_in_favourites(user, game) is False

    in_memory_repo.add_game_to_favourites(user, game)
    assert in_memory_repo.is_game_in_favourites(user, game) is True

    profile_services.remove_game_from_favourites(game.game_id, user.username, in_memory_repo)
    assert in_memory_repo.is_game_in_favourites(user, game) is False

# Test user favourites can be retrieved
def test_get_user_favourites(in_memory_repo):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(3)

    favourites = profile_services.get_user_favourites(user.username, in_memory_repo)

    assert len(favourites) == 0
    assert in_memory_repo.is_game_in_favourites(user, game) is False

    in_memory_repo.add_game_to_favourites(user, game)
    assert in_memory_repo.is_game_in_favourites(user, game) is True

    favourites = profile_services.get_user_favourites(user.username, in_memory_repo)
    assert len(favourites) == 1
    assert favourites[0].get("title") == game.title
    assert favourites[0].get("game_id") == game.game_id

    profile_services.remove_game_from_favourites(game.game_id, user.username, in_memory_repo)

    favourites = profile_services.get_user_favourites(user.username, in_memory_repo)
    assert len(favourites) == 0

def test_get_user_reviews_unknown_user(in_memory_repo):
    username = "nonexistent_user"
    with pytest.raises(UnknownUserException):
        profile_services.get_user_reviews(username, in_memory_repo)


def test_get_user_favourites_unknown_user(in_memory_repo):
    username = "nonexistent_user"
    with pytest.raises(UnknownUserException):
        profile_services.get_user_favourites(username, in_memory_repo)

# test to get user reviews
def test_get_user_reviews(in_memory_repo):
    user = User("testuser", "password")
    game = Game(1, "Test Game")

    review = Review(user, game, 4, "A great game!")
    user.add_review(review)
    in_memory_repo.add_user(user)

    reviews = profile_services.get_user_reviews("testuser", in_memory_repo)

    assert reviews[0]['comment'] == review.comment

# Test retrieving most recent review
def test_get_most_recent_review(in_memory_repo):
    test_username = "alpc"
    test_game_id = 1

    user = in_memory_repo.get_user(test_username)
    game = in_memory_repo.get_game(test_game_id)

    # Most recent review should be None if there are no reviews yet
    review = Review(user, game, 1, "New review")
    assert profile_services.get_most_recent_review(test_username, in_memory_repo) is None

    user.add_review(review)

    most_recent = profile_services.get_most_recent_review(test_username, in_memory_repo)
    assert most_recent["comment"] == "New review"

# Test retrieving most recent review with unknown user
def test_get_most_recent_review_with_nonuser_raises_error(in_memory_repo):
    username = "nonexistent_user"
    with pytest.raises(UnknownUserException):
        profile_services.get_most_recent_review(username, in_memory_repo)

# Test retrieving most recent favourite
def test_get_most_recent_favourite(in_memory_repo):
    test_username = "jess"
    test_game_id = 3

    user = in_memory_repo.get_user(test_username)
    game = in_memory_repo.get_game(test_game_id)

    # Check an empty favourites list should return None for the recent favourite
    assert profile_services.get_most_recent_favourite(test_username, in_memory_repo) is None
    user.add_favourite_game(game)

    most_recent_favourite = profile_services.get_most_recent_favourite(test_username, in_memory_repo)
    assert most_recent_favourite["title"] == game.title

# Test retrieving most recent favourite with unknown user
def test_get_most_recent_favourite_with_nonuser_raises_error(in_memory_repo):
    username = "nonexistent_user"
    with pytest.raises(UnknownUserException):
        profile_services.get_most_recent_favourite(username, in_memory_repo)

# ------------------------- #
# TESTS FOR GENRES/SERVICES #
# ------------------------- #

# Test all games for a specified genre can be retrieved
def test_can_get_games_for_specified_genre(in_memory_repo):
    action_games = genres_services.get_games_for_genre("Action", in_memory_repo)

    assert len(action_games) == 10

    simulation_games = genres_services.get_games_for_genre("Simulation", in_memory_repo)

    assert len(simulation_games) == 1


# Test all genres can be retrieved
def test_can_get_all_genres(in_memory_repo):
    all_genres = genres_services.get_genres(in_memory_repo)

    assert len(all_genres) == 6


# Test one genre object can be retrieved
def test_can_get_genre(in_memory_repo):
    genre = genres_services.get_genre("Simulation", in_memory_repo)

    assert genre is not None
    assert genre['genre_name'] == "Simulation"


# Test the total games for a genre can be retrieved
def test_get_number_of_games_for_genre(in_memory_repo):
    assert genres_services.get_number_of_games_for_genre("Action", in_memory_repo) is 10

    assert genres_services.get_number_of_games_for_genre("Simulation", in_memory_repo) is 1


# ------------------------- #
# TESTS FOR HOME/SERVICES #
# ------------------------- #

# Test home services retrieves 3 most recent games to display
def test_get_most_recent_games(in_memory_repo):
    games = home_services.get_most_recent_games(in_memory_repo)

    assert len(games) == 3
    assert games[0]['title'] == "MagicShop3D"
    assert games[0]["release_date"] == "Jun 19, 2022"
    assert games[1]['title'] == "Gladio and Glory"
    assert games[1]["release_date"] == "Mar 16, 2021"
    assert games[2]['title'] == "Bartlow's Dread Machine"
    assert games[2]['release_date'] == "Sep 29, 2020"


# ---------------------------- #
# TESTS FOR UTILITIES/SERVICES #
# ---------------------------- #

# Test genres can be sorted by popularity
def test_genres_sorted_by_popularity_for_sidebar(in_memory_repo):
    genres_sorted_by_popularity = utility_services.get_genres_sorted_by_popularity(in_memory_repo)

    # Check first 2 genres
    assert genres_sorted_by_popularity[0]['genre_name'] == "Action"
    assert genres_sorted_by_popularity[1]['genre_name'] == "Early Access"
    assert genres_services.get_number_of_games_for_genre("Early Access",
                                                         in_memory_repo) <= genres_services.get_number_of_games_for_genre(
        "Action", in_memory_repo)

    # And last 2 genres
    assert genres_sorted_by_popularity[4]['genre_name'] == "Simulation"
    assert genres_sorted_by_popularity[5]['genre_name'] == "Strategy"
    assert genres_services.get_number_of_games_for_genre("Strategy",
                                                         in_memory_repo) <= genres_services.get_number_of_games_for_genre(
        "Simulation", in_memory_repo)


app = create_app()
# Test pagination util returns correct info about pagination
def test_pagination_utility_returns_correct_info(in_memory_repo):
    numGames = games_services.get_number_of_games(in_memory_repo)
    test_limit = 2

    assert numGames == 10

    with app.test_request_context('?page=4', method='GET'):
        pagination = utility_services.get_pagination_info(numGames, test_limit)

        assert pagination['num_games_per_page'] == test_limit
        assert pagination['num_pages'] == numGames/test_limit
        assert pagination['page_number'] == 4

# Test pagination util returns the first page if the page number is invalid
def test_pagination_utility_returns_first_page_for_invalid_number(in_memory_repo):
    with app.test_request_context('?page=hello', method='GET'):
        pagination = utility_services.get_pagination_info(10)

        assert pagination['page_number'] == 1

# Test pagination util returns the first page if the page number is negative
def test_pagination_utility_returns_first_page_for_negative_number(in_memory_repo):
    with app.test_request_context('?page=-1', method='GET'):
        pagination = utility_services.get_pagination_info(10)

        assert pagination['page_number'] == 1

# ------------------------- #
# TESTS FOR SEARCH/SERVICES #
# ------------------------- #
# Test all publishers can be retrieved
def test_can_get_all_publishers(in_memory_repo):
    all_publishers = search_services.get_publishers(in_memory_repo)

    assert len(all_publishers) == 10

# Test game instance can be retrieved from a title
def test_search_retrieves_game_with_a_title(in_memory_repo):
    game = search_services.get_game_from_title("Bartlow's Dread Machine", in_memory_repo)

    assert game is not None
    assert game["title"] == "Bartlow's Dread Machine"
    assert game["price"] == 14.99


def test_search_returns_None_for_nonexistent_game(in_memory_repo):
    assert search_services.get_game_from_title("Nonexistent game", in_memory_repo) is None


# Test games can be retrieved from a publisher name
def test_search_retrieves_games_from_a_specific_publisher(in_memory_repo):
    games = search_services.get_games_for_publisher("Activision", in_memory_repo)

    assert len(games) == 1
    assert games[0]['title'] == "Call of Duty® 4: Modern Warfare®"
    assert games[0]["publisher"] == "Activision"


# If a publisher doesn't exist or doesn't have any games, search should return an empty list
def test_search_returns_empty_list_for_not_found_publisher(in_memory_repo):
    games = search_services.get_games_for_publisher("Nonexistent publisher", in_memory_repo)

    assert len(games) == 0


# Test games can be filtered by publisher
def test_games_can_be_filtered_by_publisher(in_memory_repo):
    all_games = genres_services.get_games_for_genre("Action", in_memory_repo)

    filtered_games = search_services.filter_games_by_publisher("Activision", all_games)

    assert len(filtered_games) == 1
    assert filtered_games[0].get('publisher') == "Activision"
    assert filtered_games[0].get('title') == "Call of Duty® 4: Modern Warfare®"

# Test games can be filtered by price
def test_games_can_be_filtered_by_price(in_memory_repo):
    all_games = genres_services.get_games_for_genre("Action", in_memory_repo)

    filtered_games = search_services.filter_games_by_price("10.00", all_games)

    assert len(filtered_games) == 5

    for game in filtered_games:
        assert game['price'] <= 10.00

# Test an invalid price (one that can't be converted to float) raises a search key error
def test_invalid_price_raises_error(in_memory_repo):
    all_games = games_services.get_games(in_memory_repo)

    with pytest.raises(NonExistentSearchKeyException) as excinfo:
        search_services.filter_games_by_price("invalid", all_games)

        assert excinfo == "invalid is not a valid price. Please input a number greater than 0."

# Test a negative price raises a search key error
def test_negative_price_raises_error(in_memory_repo):
    all_games = games_services.get_games(in_memory_repo)

    with pytest.raises(NonExistentSearchKeyException) as excinfo:
        search_services.filter_games_by_price("-1", all_games)

        assert excinfo == "-1 is not a valid price. Please input a number greater than 0."

# Test games can be filtered by genres
def test_games_can_be_filtered_by_genre(in_memory_repo):
    all_games = games_services.get_games(in_memory_repo)

    # Filter by action
    action_games = search_services.filter_games_by_genre(["action"], all_games)

    assert len(action_games) == 10

    for game in action_games:
        assert "Action" in game['genres']

    # Filter by a few categories
    filtered_games = search_services.filter_games_by_genre(["Simulation", "indie"], all_games)

    assert len(filtered_games) == 1

    for game in filtered_games:
        assert "Simulation" in game['genres'] or "Indie" in game["genres"]


# Test games can be retrieved from search query
def test_games_can_be_retrieved_from_search_query(in_memory_repo):
    # First test searching by publisher
    with app.test_request_context('search?term=Activision', method='GET'):
        result = search_services.get_games_from_search_query(request, in_memory_repo)

        assert len(result) == 1
        assert result[0].get('publisher') == "Activision"

    # Test searching by title
    with app.test_request_context('search?term=Call', method='GET'):
        result = search_services.get_games_from_search_query(request, in_memory_repo)

        assert len(result) == 1
        assert result[0].get('title').startswith('Call')
        assert result[0].get('title') == 'Call of Duty® 4: Modern Warfare®'

    # Test searching by genre
    with app.test_request_context('search?term=action', method='GET'):
        result = search_services.get_games_from_search_query(request, in_memory_repo)

        assert len(result) == 10


# Test an invalid search key throws an exception
def test_a_nonexistent_search_key_throws_an_error(in_memory_repo):
    with app.test_request_context('search?notasearchkey=notasearchkey', method='GET'):
        with pytest.raises(NonExistentSearchKeyException):
            search_services.get_games_from_search_query(request, in_memory_repo)

# ------------------------- #
# TESTS FOR AUTHENTICATION/SERVICES #
# ------------------------- #

# Test user can be added
def test_can_add_user(in_memory_repo):
    new_username = "Test_name"
    new_password = "Testing123"

    auth_services.add_user(new_username, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_username, in_memory_repo)

    assert user_as_dict["username"] == new_username.lower()

    # Confirm password has been encrypted
    assert user_as_dict["password"].startswith('pbkdf2:sha256:')

# Test duplicate user cannot be added
def test_cannot_add_user_with_existing_username(in_memory_repo):
    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user("Jess", "imanewpassword", in_memory_repo)

# Test valid username/password can log in user
def test_authentication_with_valid_credentials(in_memory_repo):
    try:
        auth_services.authenticate_user("jess", "cLQ^C#oFXloS", in_memory_repo)
    except AuthenticationException:
        assert False

# Test invalid password does not log in user
def test_authentication_with_invalid_password(in_memory_repo):
    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user("jess", 'abc123Invalid', in_memory_repo)

# Test nonexistent user raises exception
def test_authentication_with_nonexistent_user(in_memory_repo):
    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user("imnotauser", "notauserspassword", in_memory_repo)




