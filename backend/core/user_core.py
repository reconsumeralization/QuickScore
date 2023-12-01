import jwt
import datetime

from backend.utils.errors import NotFoundError, AuthenticationError
from backend.dao.user_dao import UserDao
from backend.schemas.user_schema import UserResponse
from backend.config.config import config

class UserCore:

    def __init__(self):
        self.user_dao = UserDao()

    def create_user(self, name: str, email: str, password: str):
        """
        Create a new user.

        Args:
            name (str): The name of the user.
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            Dict: The created user in JSON format.
        """
        user = self.user_dao.create_user(name, email, password)
        return UserResponse.model_validate(user).model_dump(mode="json")

    def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Dict: The retrieved user in JSON format.
        """
        user = self._get_user_or_raise(user_id)
        return UserResponse.model_validate(user).model_dump(mode="json")

    def get_user_by_email(self, email: str):
        """
        Retrieve a user by email.
import jwt
import datetime

from backend.utils.errors import NotFoundError, AuthenticationError
from backend.dao.user_dao import UserDao
from backend.schemas.user_schema import UserResponse
from backend.config.config import config

class UserCore:

    def __init__(self):
        self.user_dao = UserDao()

    # Create a new user
    def create_user(self, name: str, email: str, password: str):
        user = self.user_dao.create_user(name, email, password)
        user = UserResponse.model_validate(user).model_dump(mode="json")
        return user

    # Retrieve a user by ID
    def get_user_by_id(self, user_id: int):
        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User doesnot exist!")
        user = UserResponse.model_validate(user).model_dump(mode="json")
        return user

    # Retrieve a user by email
    def get_user_by_email(self, email: str):
        user = self.user_dao.get_user_by_email(email)
        if user is None:
            raise NotFoundError("User doesnot exist!")
        user = UserResponse.model_validate(user).model_dump(mode="json")
        return user

    # Update user information
        Args:
            email (str): The email of the user.

        Returns:
            Dict: The retrieved user in JSON format.
        """
        user = self._get_user_or_raise(email=email)
        return UserResponse.model_validate(user).model_dump(mode="json")

    def update_user(self, user_id: int, name: str, email: str, password: str):
        """
        Update user information.

        Args:
            user_id (int): The ID of the user.
            name (str): The new name of the user.
            email (str): The new email of the user.
            password (str): The new password of the user.

        Returns:
            Dict: The updated user in JSON format.
        """
        user = self.user_dao.update_user(user_id, name, email, password)
        return UserResponse.model_validate(user).model_dump(mode="json")

    def delete_user(self, user_id: int):
        """
        Delete a user.

        Args:
            user_id (int): The ID of the user to be deleted.

        Returns:
            bool: True if deletion is successful, False otherwise.
        """
        user = self.user_dao.delete_user(user_id)
        return UserResponse.model_validate(user).model_dump(mode="json")

    def authenticate_user(self, email, password):
        """
        Authenticate a user and generate a JWT token.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            Dict: Payload containing user information for JWT token.
        """
        user = self._get_user_or_raise(email=email)
        actual_password = str(user.__dict__["password"])
        if actual_password != password:
            raise AuthenticationError("Error in email or password!")

        secret_key = config.SECRET_KEY
        user = user.__dict__
        payload = {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
        return payload

    def _get_user_or_raise(self, user_id=None, email=None):
        """
        Get a user by ID or email, raising an error if not found.

        Args:
            user_id (int, optional): The ID of the user.
            email (str, optional): The email of the user.

        Returns:
            Dict: The retrieved user in JSON format.
        """
        user = self.user_dao.get_user_by_id(user_id) if user_id else self.user_dao.get_user_by_email(email)
        if user is None:
            raise NotFoundError("User does not exist!")
        return user
