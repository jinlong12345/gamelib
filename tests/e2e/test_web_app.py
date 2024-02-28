import pytest

from flask import session


# Test homepage renders
def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200
    assert b'CS235 2023: My Game Library' in response.data


# Test viewing all games
def test_view_all_games(client):
    # Check we can retrieve the games browse page
    response = client.get("/games/")
    assert response.status_code == 200
    assert b'Browse Games' in response.data


# Test viewing a game
def test_view_a_game(client):
    # Check we can retrieve the games browse page
    response = client.get("/games/1")
    assert response.status_code == 200
    assert b'Call of Duty' in response.data


# Test viewing all genres
def test_view_all_genres(client):
    # Check we can retrieve the genres page
    response = client.get("/genres")
    assert response.status_code == 200
    assert b'Browse all genres' in response.data


# Test viewing games for a genre
def test_view_games_for_genre(client):
    # Check we can retrieve the games browse page
    response = client.get("/genres/Action", follow_redirects=True)
    assert response.status_code == 200
    assert b'Browse Action games' in response.data


# Test search
def test_search(client):
    # Check we can retrieve the search page
    response = client.get("/search")
    assert response.status_code == 200
    assert b'Search for a game' in response.data

    # Try to search something with no results
    response = client.get("/search?term=notaterm", follow_redirects=True)
    assert b'No search results found' in response.data

    # Try to search something with hits
    response = client.get("/search?term=call", follow_redirects=True)
    assert b'Call of Duty' in response.data


# Test registration
def test_register(client):
    # Check we retrieve register page
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid username and password.
    response = client.post(
        '/authentication/register',
        data={'username': 'testRobot', 'password': 'IamATest90', 'password_confirmation': 'IamATest90'}
    )
    assert response.headers['Location'] == '/authentication/login'


@pytest.mark.parametrize(('user_name', 'password', 'password_confirmation', 'message'), (
        ('', '', '', b'Username is required'),
        ('s', '', '', b'Username must be between 3 and 256 characters long.'),
        ('test', '', '', b'Password is required'),
        ('test', 'test', 'test', b'Password must be at least 8 characters long and contain an uppercase character, '
                                 b'lowercase character, and a digit from 0-9'),
        ('new_user', 'testIng90', 'NotaMatch', b'Passwords must match'),
        ('new_user', 'testIng90', '', b'Password confirmation required'),
        ('jess', 'Test#6^0', 'Test#6^0', b'Username is already taken. Please try again.'),
))
# Test registering with invalid information
def test_register_with_invalid_input(client, user_name, password, password_confirmation, message):
    # Check that attempting to register with invalid combinations of username and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'username': user_name, 'password': password, 'password_confirmation': password_confirmation}
    )
    assert message in response.data


# Test logging in
def test_login(client, auth):
    # Check we retrieve the login page.
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    # Check successful login redirects to the homepage
    response = auth.login()
    assert response.headers["Location"] == "/"

    # Check a session has been created for the user
    with client:
        client.get('/')
        assert session["username"] == "jess"


# Test logging out
def test_logout(client, auth):
    # Login
    auth.login()

    # Log out
    with client:
        auth.logout()
        assert "username" not in session


# Test unauthenticated user cannot leave a review (tests decorator)
def test_login_required_to_review(client):
    response = client.post('/review')
    assert response.headers['Location'] == '/authentication/login'


# Test unauthenticated user cannot delete review (tests decorator)
def test_login_required_to_delete_review(client):
    response = client.get('/delete-review')
    assert response.headers['Location'] == '/authentication/login'


# Test unauthenticated user cannot view profile (tests decorator)
def test_login_required_to_view_profile(client):
    response = client.get('/profile')
    assert response.headers['Location'] == '/authentication/login'


# Test unauthenticated user cannot view favourites (tests decorator)
def test_login_required_to_see_favourites(client):
    response = client.get('/favourites')
    assert response.headers['Location'] == '/authentication/login'


# Test unauthenticated user cannot add favourite (tests decorator)
def test_login_required_to_add_favourite(client):
    response = client.get('/favourite')
    assert response.headers['Location'] == '/authentication/login'


# Test unauthenticated user cannot remove favourite (tests decorator)
def test_login_required_to_remove_favourite(client):
    response = client.get('/unfavourite')
    assert response.headers['Location'] == '/authentication/login'


# Test leaving a review
def test_review(client, auth):
    test_id = 3

    # Login a user.
    auth.login()

    # Review the game
    response = client.post(
        '/review',
        data={'game_id': test_id, 'comment': "Reviewing the third game", 'rating': 1},
        follow_redirects=True
    )

    # Check the comment has shown up (posting review should redirect user back to game page with their review on it)
    assert b'Reviewing the third game' in response.data


def test_games_with_reviews(client):
    response = client.get('/games/1')

    # Check the review comments are on the page
    assert b'Great game!' in response.data
    assert b'Hated it' in response.data
    assert b'Was really hard' in response.data


# Test removing a review
def test_removing_review(client, auth):
    test_id = 1

    response = client.get(f'/games/{test_id}')
    assert b'Great game!' in response.data

    # Login
    auth.login()

    # Delete review
    response = client.get(f"/delete_review?game_id={test_id}", follow_redirects=True)

    # Check the review comment is no longer present
    assert b'Great game!' not in response.data


@pytest.mark.parametrize(('rating', 'comment', 'messages'), (
        (90, '', (b'Please submit a rating between 0 and 5.')),
        (-1, '', (b'Please submit a rating between 0 and 5.')),
        (5, 'Te', (b'Review comments must be longer than 3 characters')),
))
# Test leaving a review with invalid input
def test_review_with_invalid_input(client, auth, rating, comment, messages):
    test_id = 3

    # Login a user.
    auth.login()

    # Attempt to review game.
    response = client.post(
        '/review',
        data={'rating': rating, 'comment': comment, 'game_id': test_id},
        follow_redirects=True
    )

    # Check that supplying invalid comment text/rating generates appropriate error messages.
    for message in messages:
        assert message in response.data


# Test viewing profile if logged in
def test_profile(client, auth):
    # Log in user
    auth.login()

    # Check the user can visit their profile
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'CS235 2023: My Game Library' in response.data
    assert b'Your user profile' in response.data


# Test adding favourite if logged in
def test_add_favourite(client, auth):
    test_game_id = 1

    # Log in user
    auth.login()

    # Attempt to add favourite game.
    response = client.get(f'/favourite?game_id={test_game_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Call of Duty' in response.data
    assert b'Remove game from favourites' in response.data


# Test removing favourite if logged in
def test_remove_favourite(client, auth):
    test_game_id = 1

    # Log in user
    auth.login()

    # Attempt to add favourite game.
    response = client.get(f'/favourite?game_id={test_game_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Remove game from favourites' in response.data
    assert b'Call of Duty' in response.data
    response = client.get(f'/unfavourite?game_id={test_game_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Add game to favourites' in response.data


# Test visiting favourites if logged in
def test_view_favourites(client, auth):
    # Log in user
    auth.login()

    # Attempt to add favourite game.
    response = client.get('/favourites')
    assert response.status_code == 200
    assert b'Favourites' in response.data
    assert b"You haven't favourited any games yet" in response.data

    client.get('/favourite?game_id=1', follow_redirects=True)
    response = client.get('/favourites')
    assert b"Call of Duty" in response.data
