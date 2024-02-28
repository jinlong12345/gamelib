import abc
from typing import List

from games.domainmodel.model import Game, Genre, Publisher, User, Review

repo_instance = None


class RepositoryException(Exception):
    def __init__(self, message=None):
        print(f'RepositoryException: {message}')


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_user(self, user: User):
        """ Add a User to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username: str) -> User:
        """ Returns the User with the named username.

         If there is no User with the given username, this method returns None.
         """
        raise NotImplementedError

    @abc.abstractmethod
    def add_game(self, game: Game):
        """ Add a game to the repository list of games """
        raise NotImplementedError

    @abc.abstractmethod
    def get_games(self) -> List[Game]:
        """ Returns the list of games """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_games(self):
        """ Returns the number of existing games in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_game(self, game_id: int) -> Game:
        """ Returns Game with id from the repository.

        If there is no Game with the given id, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_genre(self, genre: Genre):
        """ Add a genre to the repository list of genres """
        raise NotImplementedError

    @abc.abstractmethod
    def get_genre(self, genre_name: str) -> Genre:
        """ Returns Genre with name matching genre_name from the repository.

        If there is no Genre with the given genre_name, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_genres(self) -> List[Genre]:
        """ Returns the list of genres """
        raise NotImplementedError

    @abc.abstractmethod
    def get_publishers(self) -> List[Publisher]:
        """ Returns the list of publishers """
        raise NotImplementedError

    @abc.abstractmethod
    def get_games_for_genre(self, genre_name: str):
        """ Returns a list of Games with the specified genre name.

        If there are no Games with the listed Genre, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_games_for_publisher(self, publisher_name: str):
        """ Returns a list of Games with the specified publisher.

        If there are no Games with the listed Publisher, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_game_from_title(self, game_title: str) -> Game:
        """ Returns a Game object with the specified title.

        If there are no Games with the specified title, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_num_games_for_genre(self, genre_name: str):
        """ Returns the number of games associated with the specified genre in the repository """

        raise NotImplementedError

    @abc.abstractmethod
    def get_three_most_recent_games(self) -> List[Game]:
        """ Returns 3 most recent Games from the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review):
        """ Adds a Review to the repository.

        If the Review doesn't have bidirectional links with a Game and a User, this method raises a
        RepositoryException and doesn't update the repository.
        """
        if review.user is None or review not in review.user.reviews:
            raise RepositoryException('Review not correctly attached to a User')
        if review.game is None or review not in review.game.reviews:
            raise RepositoryException('Review not correctly attached to a Game')

    @abc.abstractmethod
    def get_user_review_for_game(self, user: User, game: Game):
        """ Returns a Review object with the specified user reviewer and game.

        If there are no Reviews with the specified parameters, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_review(self, review: Review):
        """ Removes a Review from the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_favourites(self, user: User):
        """ Retrieves the users favourite games """

    @abc.abstractmethod
    def get_reviews(self, user: User):
        """ Retrieves the uses favourite games """

    @abc.abstractmethod
    def add_game_to_favourites(self, user: User, game: Game):
        """ Adds the game to the user's favourites. """
        raise NotImplementedError

    def is_game_in_favourites(self, user: User, game: Game) -> bool:
        """ Checks if the game is in the user's favourites. """
        raise NotImplementedError

    def remove_game_from_favourites(self, user: User, game: Game):
        """ Removes the game from the user's favourites. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_genres(self, genres: List[Genre]):
        """ Add many genres to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_games(self, games: List[Game]):
        """ Add multiple games to the repository of games. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_publishers(self, publisher: List[Publisher]):
        """ Add multiple games to the repository of games. """
        raise NotImplementedError
