from datetime import datetime

import pytest

from games.domainmodel.model import Game, Publisher, Genre, User, Review

test_game_id = 11
test_game_title = "Test Game"
test_publisher_name = "Test Publisher"
test_genre_name = "Test Genre"
test_username = "TestUser"
@pytest.fixture
def test_game() -> Game:
    test_game_id = 11
    return Game(test_game_id, test_game_title)

@pytest.fixture
def test_user() -> User:
    test_password = "TestPassword9"
    return User(test_username, test_password)

@pytest.fixture
def test_publisher() -> Publisher:
    return Publisher(test_publisher_name)

@pytest.fixture
def test_genre() -> Genre:
    return Genre(test_genre_name)

@pytest.fixture
def test_review(test_user, test_game) -> Review:
    review = Review(test_user, test_game, 5, "Test Review")

    test_user.add_review(review)
    test_game.add_review(review)
    return review

# Repo can add a Game
def test_repository_can_add_a_game(in_memory_repo, test_game):
    in_memory_repo.add_game(test_game)

    assert in_memory_repo.get_game(test_game_id) is test_game

# Repo doesn't add object if it's not an instance of a Game
def test_repository_does_not_add_a_non_game_object(in_memory_repo, test_publisher):
    assert in_memory_repo.get_number_of_games() is 10

    in_memory_repo.add_game(test_publisher)

    assert in_memory_repo.get_number_of_games() is 10

# Repo can retrieve a Game
def test_repository_can_retrieve_a_game(in_memory_repo):
    game = in_memory_repo.get_game(1)
    assert game.title == "Call of Duty® 4: Modern Warfare®"

# Repo returns Mone if game_id is invalid
def test_repository_does_not_retrieve_a_non_existent_game(in_memory_repo):
    game = in_memory_repo.get_game('not an id')
    assert game is None

# Repo can count total number of games
def test_repository_can_get_number_of_games(in_memory_repo, test_game):
    assert in_memory_repo.get_number_of_games() is 10

    in_memory_repo.add_game(test_game)
    assert in_memory_repo.get_number_of_games() is 11

# Repo returns a list of all games
def test_repository_can_retrieve_list_of_games(in_memory_repo):
    games = in_memory_repo.get_games()

    assert len(games) is 10
    # Test equality based on id
    assert games[0] == Game(1, 'Test')
    assert games[1] == Game(2, 'Test two')

# Repo can add a Genre
def test_repository_can_add_a_genre(in_memory_repo, test_genre):
    in_memory_repo.add_genre(test_genre)
    assert in_memory_repo.get_genre(test_genre_name) is test_genre

# Repo does not add a non-Genre object to the list of genres
def test_repository_does_not_add_a_non_genre_object(in_memory_repo, test_publisher):
    genres = in_memory_repo.get_genres()

    assert len(genres) is 6

    in_memory_repo.add_genre(test_publisher)

    # Test publisher does not get added
    assert len(genres) is 6

# Repo returns a list of Genres
def test_repository_can_retrieve_list_of_genres(in_memory_repo):
    genres = in_memory_repo.get_genres()

    assert len(genres) is 6

# Repo can retrieve a singular Genre
def test_repository_can_retrieve_a_genre(in_memory_repo):
    genre = in_memory_repo.get_genre("Action")
    assert genre.genre_name == "Action"

# Repo returns None if a Genre does not exist
def test_repository_does_not_retrieve_a_non_existent_genre(in_memory_repo):
    genre = in_memory_repo.get_genre('fake genre name')
    assert genre is None

# Repo can retrieve games based on a specific Genre name
def test_repository_retrieves_games_associated_with_a_specific_genre(in_memory_repo):
    test_name = "Action"

    games = in_memory_repo.get_games_for_genre(test_name)
    genre = in_memory_repo.get_genre(test_name)

    assert len(games) is 10
    for game in games:
        assert genre in game.genres

# Repo can retrieve games associated with genres that start with the specified string (eg "Acti" for "Action" would
# still return results)
def test_repository_retrieves_games_associated_with_a_specific_incomplete_genre_string(in_memory_repo):
    test_name = "Acti"

    games = in_memory_repo.get_games_for_genre(test_name)

    assert len(games) is 10

# Repo can retrieve total number of games associated with a specific genre
def test_repository_gets_number_of_games_for_genre(in_memory_repo):
    games = in_memory_repo.get_games_for_genre("Action")

    assert len(games) is 10

# Repo can add a publisher
def test_repository_can_add_a_publisher(in_memory_repo, test_publisher):
    in_memory_repo.add_publisher(test_publisher)
    assert in_memory_repo.get_publisher(test_publisher_name) is test_publisher

# Repo can retrieve a publisher
def test_repository_can_retrieve_a_publisher(in_memory_repo, test_publisher):
    in_memory_repo.add_publisher(test_publisher)

    publisher = in_memory_repo.get_publisher(test_publisher_name)
    assert publisher is test_publisher

# Repo can retrieve all publishers
def test_repository_can_retrieve_publishers(in_memory_repo, test_publisher):
    publishers = in_memory_repo.get_publishers()

    assert len(publishers) == 10

    in_memory_repo.add_publisher(test_publisher)

    assert len(publishers) == 11


# Repo can retrieve games associated with a given publisher
def test_repository_retrieves_games_associated_with_a_specific_publisher(in_memory_repo):
    games = in_memory_repo.get_games_for_publisher("Activision")

    assert len(games) is 1
    assert games[0].game_id is 1
    assert games[0].title == "Call of Duty® 4: Modern Warfare®"

# Repo retrieves games even if the publisher string is incomplete, eg "Acti" for Activision would still return results)
def test_repository_retrieves_games_even_if_publisher_name_is_incomplete(in_memory_repo):
    games = in_memory_repo.get_games_for_publisher("Acti")

    assert len(games) is 1
    assert games[0].game_id is 1
    assert games[0].title == "Call of Duty® 4: Modern Warfare®"

# Repo can retrieve game with a given title
def test_repository_retrieves_game_with_given_title(in_memory_repo, test_game):
    in_memory_repo.add_game(test_game)

    assert in_memory_repo.get_game_from_title(test_game_title) is test_game

# Even if the title is incomplete, the repo can still retrieve the game
def test_repository_retrieves_game_with_incomplete_title(in_memory_repo, test_game):
    in_memory_repo.add_game(test_game)

    assert in_memory_repo.get_game_from_title(test_game_title[0:5]) is test_game

# Repo returns None if the title is invalid
def test_repository_returns_none_if_game_with_title_does_not_exist(in_memory_repo):
    assert in_memory_repo.get_game_from_title("doesn't exist") is None

# Repo retrieves 3 most recent games, these should be sorted by date
def test_repository_retrieves_three_most_recent_games(in_memory_repo):
    games = in_memory_repo.get_three_most_recent_games()

    date_format = "%b %d, %Y"

    assert len(games) is 3
    assert games[0].game_id is 5
    assert games[0].release_date == "Jun 19, 2022"
    assert datetime.strptime(games[0].release_date, date_format) > datetime.strptime(games[1].release_date, date_format)
    assert datetime.strptime(games[1].release_date, date_format) > datetime.strptime(games[2].release_date, date_format)

def test_repository_populates_variables_using_dataset(in_memory_repo):
    games = in_memory_repo.get_games()
    genres = in_memory_repo.get_genres()

    assert len(games) is 10
    assert len(genres) is 6

# Repo can add a User
def test_repository_can_add_a_user(in_memory_repo, test_user):
    in_memory_repo.add_user(test_user)

    assert in_memory_repo.get_user(test_username) is test_user

# Repo does not add user if not a valid User object
def test_repository_does_not_add_non_user_object(in_memory_repo, test_publisher):
    in_memory_repo.add_user(test_publisher)

    assert in_memory_repo.get_user(test_publisher_name) is None

# Repo can retrieve a user
def test_repository_can_retrieve_a_user(in_memory_repo, test_user):
    in_memory_repo.add_user(test_user)

    user = in_memory_repo.get_user(test_username)

    assert user is test_user

# Repo can add a review
def test_repository_can_add_review(in_memory_repo, test_review, test_user, test_game):
    in_memory_repo.add_review(test_review)

    reviews = in_memory_repo.get_reviews()

    assert len(reviews) == 1

    review = in_memory_repo.get_user_review_for_game(test_user, test_game)

    assert review is test_review

# Test repo can retrieve review for given user and game
def test_repository_can_add_review(in_memory_repo, test_review, test_user, test_game):
    in_memory_repo.add_review(test_review)

    review = in_memory_repo.get_user_review_for_game(test_user, test_game)

    assert review is test_review


# Repo can remove review
def test_repository_can_remove_review(in_memory_repo, test_user, test_game, test_review):
    in_memory_repo.add_review(test_review)

    reviews = in_memory_repo.get_reviews()

    assert len(reviews) == 7

    in_memory_repo.remove_review(test_review)

    assert len(in_memory_repo.get_reviews()) == 6

# Repo adds a valid favourite game to the user's list of favourites
def test_repository_adds_favourite_game(in_memory_repo, test_game):
    user = in_memory_repo.get_user("jess")

    assert len(user.favourite_games) == 0

    in_memory_repo.add_game_to_favourites(user, test_game)

    assert len(user.favourite_games) == 1

# Repo does not add an invalid game to the user's list of favourites
def test_repository_doesnt_add_invalid_favourite_game(in_memory_repo):
    user = in_memory_repo.get_user("jess")

    assert len(user.favourite_games) == 0

    in_memory_repo.add_game_to_favourites(user, "notagame")

    assert len(user.favourite_games) == 0

# Repo does not add duplicate game to user's list of favourites
def test_repository_doesnt_add_duplicate_favourite_game(in_memory_repo, test_game):
    user = in_memory_repo.get_user("jess")

    assert len(user.favourite_games) == 0

    in_memory_repo.add_game_to_favourites(user, test_game)

    assert len(user.favourite_games) == 1

    in_memory_repo.add_game_to_favourites(user, test_game)

    assert len(user.favourite_games) == 1

# Repo correctly identifies if a game is in a user's favourites
def test_repository_checks_if_game_is_favourited(in_memory_repo):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(1)

    assert len(user.favourite_games) == 0

    assert in_memory_repo.is_game_in_favourites(user, game) is False

    in_memory_repo.add_game_to_favourites(user, game)

    assert len(user.favourite_games) == 1

    assert in_memory_repo.is_game_in_favourites(user, game) is True

# Repo removes game from the user's list of favourites if the game is there
def test_repository_removes_favourite_game(in_memory_repo):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(1)

    assert len(user.favourite_games) == 0

    in_memory_repo.add_game_to_favourites(user, game)

    assert len(user.favourite_games) == 1

    in_memory_repo.remove_game_from_favourites(user, game)

    assert len(user.favourite_games) == 0

# Repo does nothing if the game is not in the favourites
def test_repository_removes_favourite_game(in_memory_repo, test_game):
    user = in_memory_repo.get_user("jess")
    game = in_memory_repo.get_game(1)

    assert len(user.favourite_games) == 0

    in_memory_repo.add_game_to_favourites(user, game)

    assert len(user.favourite_games) == 1

    in_memory_repo.remove_game_from_favourites(user, test_game)

    assert len(user.favourite_games) == 1