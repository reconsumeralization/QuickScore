from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import exc

from backend.utils.db_conn import conn
from backend.utils.errors import DatabaseError, DuplicateError, NotFoundError
from backend.models.models import StudentModel, AnswerModel

class StudentDao:
    """
    Data Access Object for Student related operations
    """
    def __init__(self):
        self.db: Session = conn.get_db()

    def create_student(self, name: str, roll_no: str, email: str, user_id: int) -> StudentModel:
        """
        Create a new student record in the database
        """
        try:
            student = StudentModel(name=name, roll_no=roll_no, email=email, user_id=user_id)
            self.db.add(student)
            self.db.flush()
            self.db.refresh(student)
        except exc.IntegrityError:
            raise DuplicateError("A student with the same name, roll number, email, or user id already exists.")
        except Exception:
            raise DatabaseError("An error occurred while trying to create a new student.")
        return student

    def get_student_by_id(self, student_id: int) -> Optional[StudentModel]:
        """
        Retrieve a student record by its id
        """
        student = self.db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if student is None:
            raise NotFoundError(f"A student with id {student_id} does not exist.")
        return student

    def get_students_by_user_id(self, user_id: int) -> List[StudentModel]:
        """
        Retrieve all student records associated with a specific user id
        """
        try:
            students = self.db.query(StudentModel).filter(StudentModel.user_id == user_id).all()
        except Exception:
            raise DatabaseError(f"An error occurred while trying to retrieve students for user id {user_id}.")
        return students

    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student record and all its associated answer records
        """
        student = self.db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if student is None:
            raise NotFoundError(f"A student with id {student_id} does not exist.")
        self.db.query(AnswerModel).filter(AnswerModel.student_id == student.id).delete()
        self.db.delete(student)
        return True
