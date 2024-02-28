"""Initialize Flask app."""
import os
from pathlib import Path

from flask import Flask

import games.adapters.repository as repo

from games.adapters import memory_repository, database_repository, repository_populate

from sqlalchemy import create_engine, inspect

from sqlalchemy.orm import sessionmaker, clear_mappers

from sqlalchemy.pool import NullPool

from games.adapters.orm import map_model_to_tables, metadata


def create_app(test_config=None):
    """Construct the core application."""
    # Create the Flask app object.
    app = Flask(__name__)
    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = Path('games') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    # Create the MemoryRepository implementation for a memory-based repository

    if app.config['REPOSITORY'] == 'memory':
        repo.repo_instance = memory_repository.MemoryRepository()
        # Fill the repository from the provided CSV file
        repository_populate.populate(data_path, repo.repo_instance)

    elif app.config['REPOSITORY'] == 'database':
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        database_echo = app.config['SQLALCHEMY_ECHO']

        # Create the database engine.
        database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                        echo=database_echo)

        # Create the database session factory using sessionmaker.
        session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)

        # Create the SQLAlchemy DatabaseRepository instance for a database-based repository.
        repo.repo_instance = database_repository.SqlAlchemyRepository(session_factory)

        if app.config['TESTING'] == 'True' or len(database_engine.table_names()) == 0:
            print("REPOPULATING DATABASE...")
            # For testing, or first-time use of the web application, reinitialise the database.
            clear_mappers()
            metadata.create_all(database_engine)  # Conditionally create database tables.
            for table in reversed(metadata.sorted_tables):  # Remove any data from the tables.
                with database_engine.connect() as conn:
                    conn.execute(table.delete())

            # Generate mappings that map domain model classes to the database tables.
            map_model_to_tables()

            repository_populate.populate(data_path, repo.repo_instance)
            print("REPOPULATING DATABASE... FINISHED")

            app.session_factory = session_factory

        else:
            # Solely generate mappings that map domain model classes to the database tables.
            map_model_to_tables()

    # Register blueprints
    with app.app_context():
        from .home import home
        app.register_blueprint(home.home_blueprint)

        # Blueprint associated with viewing all/individual games
        from .browse import browse
        app.register_blueprint(browse.browse_blueprint)

        # Blueprint associated with browsing by genre
        from .genres import genres
        app.register_blueprint(genres.genres_blueprint)

        # Utilities for each page, i.e. selecting top genres to display in sidebar
        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)

        # Blueprint for search
        from .search import search
        app.register_blueprint(search.search_blueprint)

        # Blueprint for authentication
        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        # Blueprint for profile
        from .profile import profile
        app.register_blueprint(profile.profile_blueprint)
    return app
