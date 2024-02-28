import csv
from pathlib import Path
from datetime import date, datetime

from werkzeug.security import generate_password_hash

from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Publisher, Genre, User, Game, Review, Wishlist, make_review, delete_review


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_games(data_path: Path, repo: AbstractRepository):
    games_filename = str(Path(data_path) / "games.csv")
    for data_row in read_csv_file(games_filename):
        # Extract game data from the CSV row
        game_id = int(data_row[0])
        game_title = data_row[1]
        publisher_name = data_row[16]
        release_date = data_row[2]
        price = float(data_row[3]) if data_row[3] else None
        description = data_row[4] if data_row[4] else None
        image_url = data_row[8] if data_row[8] else None
        website_url = data_row[9] if data_row[9] else None
        genre_names = [genre.strip() for genre in data_row[18].split(',') if genre.strip()]

        # Create a game object
        game = Game(game_id, game_title)

        # Set game attributes
        game.publisher = Publisher(publisher_name)
        game.release_date = release_date
        game.price = price
        game.description = description
        game.image_url = image_url
        game.website_url = website_url

        # Add genres to the game
        for genre_name in genre_names:
            genre = Genre(genre_name)
            game.add_genre(genre)

        # Add the game to the repository
        repo.add_game(game)


def load_users(data_path: Path, repo: AbstractRepository):
    users_filename = str(Path(data_path) / "users.csv")
    for data_row in read_csv_file(users_filename):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )

        repo.add_user(user)


# Load reviews from CSV file for testing/dev purposes

def load_reviews(data_path: Path, repo: AbstractRepository):
    reviews_filename = str(Path(data_path) / "reviews.csv")
    for data_row in read_csv_file(reviews_filename):
        review = make_review(
            review_text=data_row[3],
            rating=int(data_row[4]),
            user=repo.get_user(data_row[2]),
            game=repo.get_game(int(data_row[1])),
        )
        repo.add_review(review)
