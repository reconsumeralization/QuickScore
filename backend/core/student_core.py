import jwt
import datetime

from backend.utils.errors import NotFoundError, AuthenticationError
from backend.dao.student_dao import StudentDao
from backend.schemas.student_schema import StudentResponse, CreateStudent
from backend.config.config import config

class StudentCore:

    def __init__(self):
        self.student_dao = StudentDao()

    def create_student(self, input: CreateStudent):
        """
        Create a new student.

        Parameters:
        - input (CreateStudent): Student details.

        Returns:
        - dict: Created student details.
        """
        student = self.student_dao.create_student(
            name=input["name"],
            roll_no=input["roll_no"],
            email=input["email"],
            user_id=input["user_id"]
        )
        return StudentResponse.model_validate(student).model_dump(mode="json")

    def get_student_by_id(self, student_id: int):
        """
        Retrieve a student by ID.

        Parameters:
        - student_id (int): Student ID.

        Returns:
        - dict: Student details.
        """
        student = self.student_dao.get_student_by_id(student_id)
        return StudentResponse.model_validate(student).model_dump(mode="json")

    def get_students_by_user_id(self, user_id: int):
        """
        Retrieve students by user ID.

        Parameters:
        - user_id (int): User ID.

        Returns:
        - list: List of student details.
        """
        students = self.student_dao.get_students_by_user_id(user_id)
        return [StudentResponse.model_validate(student).model_dump(mode="json") for student in students]

    def delete_student(self, student_id: int):
        """
        Delete a student.

        Parameters:
        - student_id (int): Student ID.

        Returns:
        - bool: True if deletion is successful.
        """
        self.student_dao.delete_student(student_id)
        return True
