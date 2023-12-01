from typing import List, Optional, Dict
from uuid import uuid4

from backend.dao.context_dao import ContextDao
from backend.schemas.context_schema import ContextResponse, CreateContext
from backend.rag_models.vector_store import VectorDB
from backend.utils.errors import BadRequestError, ModelError


class ContextCore:
    def __init__(self) -> None:
        self.context_dao = ContextDao()

    def create_context(self, input: CreateContext, filename: str, context_pdf: Optional[str] = None) -> Dict:
        """
        Create a context and store it in the database.

        Args:
            input (CreateContext): The input data for creating the context.
            filename (str): The name of the file.
            context_pdf (Optional[str]): The PDF content of the context.

        Returns:
            Dict: The created context in JSON format.
        """
        if not context_pdf:
            raise BadRequestError("Could not parse the PDF")

        context_key = self._generate_context_key()
        vector_db = VectorDB()

        if vector_db.embed_and_store(context_pdf, context_key):
            context = self._store_context(input, filename, context_key)
            return ContextResponse.model_validate(context).model_dump(mode="json")
        else:
            raise ModelError("Could not process the context PDF!")

    def get_context_by_id(self, context_id: int) -> Dict:
        """
        Retrieve a context by its ID.

        Args:
            context_id (int): The ID of the context.

        Returns:
            Dict: The retrieved context in JSON format.
        """
        context = self.context_dao.get_context_by_id(context_id)
        return ContextResponse.model_validate(context).model_dump(mode="json")

    def get_contexts_by_user_id(self, user_id: int) -> List[Dict]:
        """
        Retrieve all contexts for a given user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[Dict]: List of contexts in JSON format.
        """
        contexts = self.context_dao.get_contexts_by_user_id(user_id)
        return [ContextResponse.model_validate(context).model_dump(mode="json") for context in contexts]

    def delete_context(self, context_id: int) -> bool:
        """
        Delete a context by its ID.

        Args:
            context_id (int): The ID of the context to be deleted.

        Returns:
            bool: True if deletion is successful, False otherwise.
        """
        self.context_dao.delete_context(context_id)
        return True

    def _generate_context_key(self) -> str:
        """
        Generate a unique context key.

        Returns:
            str: The generated context key.
        """
        uuid_str = str(uuid4()).replace('-', '')
        return f"CONTEXT{uuid_str[0].upper()}{uuid_str[1:]}"

    def _store_context(self, input: CreateContext, filename: str, context_key: str) -> Dict:
        """
        Store the context in the database.

        Args:
            input (CreateContext): The input data for creating the context.
            filename (str): The name of the file.
            context_key (str): The unique key for the context.

        Returns:
            Dict: The stored context.
        """
        return self.context_dao.create_context(
            name=input["name"],
            comments=input["comments"],
            context_key=context_key,
            user_id=input["user_id"],
            filename=filename
        )
