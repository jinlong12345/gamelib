from games.adapters.repository import AbstractRepository
from games.browse.services import games_to_dict


# Retrieve 3 most recent games to display on homepage
def get_most_recent_games(repo: AbstractRepository):
    games = repo.get_three_most_recent_games()

    # Turn games into dict
    return games_to_dict(games)