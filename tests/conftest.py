import pytest

from games import create_app
# from games import create_app
from games.adapters import memory_repository
from games.adapters.memory_repository import MemoryRepository

from utils import get_project_root

# CSV files in the test folder are different from the actual CSV data in the app
# Tests are written against the CSV files in tests/data. This data path is used to override the default path for testing
TEST_DATA_PATH = get_project_root() / "tests" / "data"

@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    memory_repository.populate(repo, TEST_DATA_PATH)
    return repo

@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,                        # Set to True during testing.
        'TEST_DATA_PATH': TEST_DATA_PATH,       # Path for loading test data into the repo
        'WTF_CSRF_ENABLED': False               # test_client will not send a CSRF token, so disable validation.
    })

    return my_app.test_client()

class AuthenticationManager:
    def __init__(self, client):
        self.__client = client

    def login(self, username="jess", password="cLQ^C#oFXloS"):
        return self.__client.post(
            'authentication/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self.__client.get('/authentication/logout')

@pytest.fixture
def auth(client):
    return AuthenticationManager(client)