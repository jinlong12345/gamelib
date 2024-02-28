import csv
from abc import ABC
from datetime import datetime
from pathlib import Path

from typing import List
from bisect import insort_left

from games.adapters.datareader.csvdatareader import GameFileCSVReader
from games.adapters.repository import AbstractRepository, RepositoryException
from games.domainmodel.model import Game, Genre, Publisher, User, Review, make_review

from werkzeug.security import generate_password_hash


class MemoryRepository(AbstractRepository, ABC):
    def __init__(self):
        self.__games = list()
        self.__genres = list()
        self.__publishers = list()
        self.__users = list()
        self.__reviews = list()

    def add_game(self, game: Game):
        if isinstance(game, Game):
            # Keep game list sorted alphabetically by id when inserting game
            # Games will be sorted by game_id due to __lt__ method of the Game class
            insort_left(self.__games, game)

    def get_game(self, game_id: int) -> Game | None:
        return next((g for g in self.__games if g.game_id == game_id), None)

    def get_games(self) -> List[Game]:
        return self.__games

    def get_number_of_games(self):
        return len(self.__games)

    def add_genre(self, genre: Genre):
        if isinstance(genre, Genre):
            insort_left(self.__genres, genre)

    def get_genres(self) -> List[Genre]:
        return self.__genres

    def get_publishers(self) -> List[Publisher]:
        return self.__publishers

    def get_genre(self, genre_name: str) -> Genre:
        return next((g for g in self.__genres if g.genre_name == genre_name), None)

    def add_publisher(self, publisher: Publisher):
        if isinstance(publisher, Publisher):
            # Keep game list sorted alphabetically by id when inserting game
            # Games will be sorted by game_id due to __lt__ method of the Game class
            insort_left(self.__publishers, publisher)

    def get_publisher(self, publisher_name: str) -> Publisher:
        return next((p for p in self.__publishers if p.publisher_name.lower() == publisher_name.lower()), None)

    # Search methods
    def get_games_for_genre(self, genre_name: str) -> List[Game]:
        # Linear search to find the first occurrence of a Genre with the name genre_name
        genre = next((g for g in self.__genres if g.genre_name.lower().startswith(genre_name.lower())), None)

        def has_genre(game: Game):
            if genre in game.genres:
                return True

            return False

        # Return a list of the ids of games associated with the genre
        if genre is not None:
            games = list(filter(has_genre, self.__games))
        else:
            # No Genre with given genre_name, so return an empty list
            games = list()

        return games

    def get_games_for_publisher(self, publisher_name: str) -> List[Game]:
        # Linear search to find the first occurrence of a Publisher with the given publisher_name
        publisher = next((p for p in self.__publishers if p.publisher_name.lower().startswith(publisher_name.lower())),
                         None)

        def has_publisher(game: Game):
            if game.publisher is publisher:
                return True

            return False

        # Return a list of the ids of games associated with the publisher
        if publisher is not None:
            games = list(filter(has_publisher, self.__games))
        else:
            # No publisher with given publisher_name, so return an empty list
            games = list()

        return games

    def get_game_from_title(self, title: str) -> Game:
        # Linear search to find the first occurrence of a Game with the given title
        game = next((g for g in self.__games if g.title.lower().startswith(title.lower())), None)

        return game

    def get_num_games_for_genre(self, genre_name: str):
        return len(self.get_games_for_genre(genre_name))

    def get_three_most_recent_games(self) -> List[Game]:
        games = list()

        if len(self.__games) > 0:
            # Sort games by release_date (most recent), then slice & return the first 3
            games = self.__games
            games.sort(key=lambda g: datetime.strptime(g.release_date, "%b %d, %Y"), reverse=True)
            return games[0:3]

        # Return an empty list if there are no games
        return games

    def add_user(self, user: User):
        if isinstance(user, User):
            self.__users.append(user)

    def get_user(self, username) -> User:
        return next((u for u in self.__users if u.username == username.lower()), None)

    def add_review(self, review: Review):
        # call parent class first, add_review relies on implementation of code common to all derived classes
        super().add_review(review)
        self.__reviews.append(review)

    def get_user_review_for_game(self, user: User, game: Game):
        # Linear search to find the first occurrence of a Review in the user reviews associated with the given game
        review = next((r for r in self.__reviews if r.game == game and r.user == user), None)

        return review

    def get_reviews(self, user: User):
        return self.__reviews

    def remove_review(self, review: Review):
        self.__reviews.remove(review)

    # Helper to check if a game is in the user's favourites already
    def is_game_in_favourites(self, user: User, game: Game) -> bool:
        if isinstance(user, User) and isinstance(game, Game):
            return game in user.favourite_games

        return False

    def add_game_to_favourites(self, user: User, game: Game):
        if isinstance(user, User) and isinstance(game, Game):
            if not self.is_game_in_favourites(user, game):
                user.add_favourite_game(game)

    def remove_game_from_favourites(self, user: User, game: Game):
        if self.is_game_in_favourites(user, game):
            user.remove_favourite_game(game)

    def add_multiple_games(self, games: List[Game]):
        for game in games:
            self.add_game(game)

    def add_multiple_genres(self, genres: List[Genre]):
        for genre in genres:
            self.add_genre(genre)

    def get_favourites(self, user: User):
        return user.favourite_games

    def add_multiple_publishers(self, publisher: List[Publisher]):
        for p in publisher:
            self.add_publisher(p)
