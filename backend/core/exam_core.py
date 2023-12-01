import jwt
import datetime
import json
from backend.utils.errors import NotFoundError, AuthenticationError, InternalServerError, BadRequestError
from backend.dao.exam_dao import ExamDao
from backend.schemas.exam_schema import ExamResponse
from backend.config.config import config
from backend.rag_models.question_splitter import QuestionSplitter

class ExamCore:

    def __init__(self):
        self.exam_dao = ExamDao()

    def create_exam(self, input: ExamResponse, filename: str, answer_key: str = ""):
        """
        Create a new exam.

        Parameters:
        - input (ExamResponse): Exam details.
        - filename (str): File name.
        - answer_key (str, optional): Answer key. Defaults to "".

        Returns:
        - dict: Created exam details.
        """
        if answer_key == "":
            raise BadRequestError("Could not parse the pdf")

        qs = QuestionSplitter()
        json_answer_key = qs.splitter(answer_key)
        exam = self.exam_dao.create_exam(
            name=input["name"],
            conducted_date=input["conducted_date"],
            description=input["description"],
            total_marks=input["total_marks"],
            user_id=input["user_id"],
            answer_key=json_answer_key,
            context_id=input["context_id"],
            filename=filename
        )
        return ExamResponse.model_validate(exam).model_dump(mode="json")

    def get_exam_by_id(self, exam_id: int):
        """
        Retrieve an exam by ID.

        Parameters:
        - exam_id (int): Exam ID.

        Returns:
        - dict: Exam details.
        """
        exam = self.exam_dao.get_exam_by_id(exam_id)
        if not exam:
            raise NotFoundError("Exam does not exist!")
        exam_obj = exam[0]
        return ExamResponse.model_validate(exam_obj).model_dump(mode="json")

    def get_exams_by_user_id(self, user_id: int):
        """
        Retrieve exams by user ID.

        Parameters:import jwt
import datetime
import json
from backend.utils.errors import NotFoundError, AuthenticationError, InternalServerError, BadRequestError
from backend.dao.exam_dao import ExamDao
from backend.schemas.exam_schema import ExamResponse
from backend.config.config import config
from backend.rag_models.question_splitter import QuestionSplitter


class ExamCore:

    def __init__(self):
        self.exam_dao = ExamDao()

    # Create a new user
    def create_exam(self, input: ExamResponse, filename:str, answer_key: str = ""):
        if answer_key == "":
            raise BadRequestError("Could not parse the pdf")

        qs = QuestionSplitter()
        json_answer_key = qs.splitter(answer_key)
        exam = self.exam_dao.create_exam(name= input["name"], conducted_date=input["conducted_date"], description=input["description"], total_marks=input["total_marks"], user_id=input["user_id"], answer_key=json_answer_key, context_id=input["context_id"], filename=filename)
        exam = ExamResponse.model_validate(exam).model_dump(mode="json")
        return exam

    # Retrieve a user by ID
    def get_exam_by_id(self, id: int):
        exam = self.exam_dao.get_exam_by_id(id)
        if exam is None:
            raise NotFoundError("Exam doesnot exist!")
        exam_obj = exam[0]
        exam_res = ExamResponse.model_validate(exam_obj).model_dump(mode="json")
        return exam_res

    # Retrieve a user by email
        - user_id (int): User ID.

        Returns:
        - list: List of exam details.
        """
        exams = self.exam_dao.get_exams_by_user_id(user_id)
        return [ExamResponse.model_validate(exam[0]).model_dump(mode="json") for exam in exams]

    def delete_exam(self, exam_id: int):
        """
        Delete an exam.

        Parameters:
        - exam_id (int): Exam ID.

        Returns:
        - bool: True if deletion is successful.
        """
        self.exam_dao.delete_exam(exam_id)
        return True

    def __is_valid_json(self, input_string):
        try:
            json.loads(input_string)
            return True
        except ValueError as error:
            print(error)
            return False
