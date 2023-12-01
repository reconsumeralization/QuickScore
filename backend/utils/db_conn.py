from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

from backend.config.config import config
from backend.utils.errors import InternalServerError, DatabaseError

Base = declarative_base()

class DBConn:
    """
    A singleton class that provides a connection to a database using SQLAlchemy.
    """
    _instance = None
    _db_url: str
    _session_local: sessionmaker
    _engine = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._db_url = "sqlite:///mydatabase.db"

    def setup_server(self) -> None:
        """
        Sets up the database connection and creates the database if it does not exist.
        """
        self._engine = create_engine(self._db_url, connect_args={}, future=True)
        self._session_local = sessionmaker(autocommit=False, autoflush=False, bind=self._engine, future=True)
        self._create_db_if_not_exists()
        self._create_all()

    def _create_db_if_not_exists(self) -> None:
        """
        Creates the database if it does not exist.
        """
        try:
            if not database_exists(self._engine.url):
                create_database(self._engine.url)
                print("Database Created Successfully!!")
        except Exception as error:
            raise InternalServerError("There has been a problem in checking the connection for the db.") from error

    def _create_all(self) -> None:
        """
        Creates all the tables in the database.
        """
        Base.metadata.create_all(bind=self._engine)

    def get_db_url(self) -> str:
        """
        Returns the database URL.
        """
        return self._db_url

    def get_db(self):
        """
        Returns a new database session.
        """
        try:from backend.config.config import config  # Correct import name

Base = declarative_base()


class Database:
    """
    A singleton class that provides a connection to a database using SQLAlchemy.
    """

    _instance = None
    _db_url = config.DATABASE_URL  # Correct reference to the config object
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


            db = self._session_local()
            return db
        except Exception as error:
            raise DatabaseError("Error while connecting to database!!") from error

    def close_all_connections(self) -> None:
        """
        Closes all the connections to the database.
        """
        if self._engine is not None:
            self._engine.dispose()
