from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

from backend.config.config import config
from backend.utils.errors import databaseError

Base = declarative_base()


class Database:
    """
    A singleton class that provides a connection to a database using SQLAlchemy.
    """

    _instance = None
    _db_url = Config.DATABASE_URL
    _session_local = None
    _engine = None

    def __new__(cls):
        """
        Overrides __new__ method to implement the singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes a Database object with a database URL.
        """

    def setup_server(self):
        """
        Sets up the database connection and creates the database if it does not exist.
        """
        self._engine = create_engine(self._db_url, future=True)
        self._session_local = sessionmaker(autocommit=False, autoflush=False, bind=self._engine, future=True)
        self._create_db_if_not_exists()

    def _create_db_if_not_exists(self):
        """
        Creates the database if it does not exist.
        """
        if not database_exists(self._db_url):
            create_database(self._db_url)

    def create_all_tables(self):
        """
        Creates all the tables in the database.
        """
        Base.metadata.create_all(bind=self._engine)

    def get_db_url(self):
        """
        Returns the database URL.
        """
        return self._db_url

    def get_db(self):
        """
        Returns a new database session.
        """
        try:
            db = self._session_local()
            return db
        except Exception as error:
            raise DatabaseError("Error while connecting to the database") from error

    def close_all_connections(self):
        """
        Closes all the connections to the database.
        """
        if self._engine is not None:
            self._engine.dispose()
