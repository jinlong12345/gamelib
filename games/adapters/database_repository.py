from abc import ABC
from typing import List

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func, desc

from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Game, Publisher, Genre, User, Review, Wishlist
from games.adapters.orm import favourite_games_table


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository, ABC):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def get_session(self):
        return self._session_cm.session

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    # region Game_data
    def get_games(self) -> List[Game]:
        games = self._session_cm.session.query(Game).order_by(Game._Game__game_id).all()
        return games

    def get_game(self, game_id: int) -> Game:
        game = None
        try:
            game = self._session_cm.session.query(
                Game).filter(Game._Game__game_id == game_id).one()
        except NoResultFound:
            print(f'Game {game_id} was not found')

        return game

    def add_game(self, game: Game):
        with self._session_cm as scm:
            scm.session.merge(game)
            scm.commit()

    def add_multiple_games(self, games: List[Game]):
        with self._session_cm as scm:
            for game in games:
                scm.session.merge(game)
            scm.commit()

    def get_number_of_games(self):
        total_games = self._session_cm.session.query(Game).count()
        return total_games

    # endregion

    # region Publisher data
    def get_publishers(self) -> List[Publisher]:
        publishers = self._session_cm.session.query(Publisher).all()
        return publishers

    def add_publisher(self, publisher: Publisher):
        with self._session_cm as scm:
            scm.session.merge(publisher)
            scm.commit()

    def add_multiple_publishers(self, publishers: List[Publisher]):
        with self._session_cm as scm:
            for publisher in publishers:
                scm.session.merge(publisher)
            scm.commit()

    def get_number_of_publishers(self) -> int:
        pass

    # endregion

    # region Genre_data
    def get_genres(self) -> List[Genre]:
        return self._session_cm.session.query(Genre).all()

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.merge(genre)
            scm.commit()

    def add_multiple_genres(self, genres: List[Genre]):
        with self._session_cm as scm:
            for genre in genres:
                scm.session.merge(genre)
            scm.commit()

    # endregion

    def search_games_by_title(self, title_string: str) -> List[Game]:
        pass

    def add_game_to_favourites(self, user: User, game: Game):
        with self._session_cm as scm:
            user.add_favourite_game(game)
            scm.commit()

    def add_review(self, review: Review):
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_games_for_genre(self, genre_name: str) -> List[Game]:
        games = self._session_cm.session.query(Game) \
            .join(Game._Game__genres).filter(Genre._Genre__genre_name == genre_name).all()
        return games


    def get_game_from_title(self, title: str) -> Game:
        # Perform a case-insensitive search for a game with a title that contains the provided title string
        games = self._session_cm.session.query(Game).filter(Game._Game__game_title.ilike(f'%{title}%')).all()

        if games:
            return games[0]  # Return the first matching game
        else:
            return None  # Return None if no matching game is found

    def get_games_for_publisher(self, publisher_name: str) -> List[Game]:
        # Perform a case-insensitive search for a publisher with the given name
        publisher_name = publisher_name.lower()
        publisher = self._session_cm.session.query(Publisher).filter(
            func.lower(Publisher._Publisher__publisher_name) == publisher_name).first()

        if publisher is not None:
            # Retrieve games associated with the publisher
            games = publisher.games
        else:
            # No publisher with the given name, so return an empty list
            games = []

        return games

    def get_genre(self, genre_name: str) -> Genre:
        # Perform a case-insensitive search for a genre with the given name
        genre_name = genre_name.lower()
        genre = self._session_cm.session.query(Genre).filter(func.lower(Genre._Genre__genre_name) == genre_name).first()
        return genre

    def get_num_games_for_genre(self, genre_name: str):
        return len(self.get_games_for_genre(genre_name))

    def get_three_most_recent_games(self) -> List[Game]:
        games = self._session_cm.session.query(Game).order_by(desc(Game._Game__release_date)).limit(3).all()
        return games

    def get_user(self, username) -> User:
        user = self._session_cm.session.query(User).filter(User._User__username == username.lower()).first()
        return user

    def get_user_review_for_game(self, user: User, game: Game):
        review = self._session_cm.session.query(Review).filter( Review._Review__user == user, Review._Review__game == game ).first()
        return review

    def remove_review(self, review: Review):
        with self._session_cm as scm:
            scm.session.delete(review)
            scm.commit()

    def get_favourites(self, user: User) -> List[Game]:
        favourites = self._session_cm.session.query(Game).join(favourite_games_table).filter(favourite_games_table.c.username == user.username).all()
        return favourites

    def get_reviews(self, user: User):
        return self._session_cm.session.query(Review).all()

    def is_game_in_favourites(self, user: User, game: Game) -> bool:
        return game in user.favourite_games

    def remove_game_from_favourites(self, user: User, game: Game):
        with self._session_cm as scm:
            user.remove_favourite_game(game)
            scm.commit()

