from sqlalchemy.orm import Session
from sqlalchemy import exc
import logging

from backend.utils.db_conn import conn
from backend.utils.errors import DatabaseError, DuplicateError, NotFoundError
from backend.models.models import StudentModel, AnswerModel

class StudentDao:
    def __init__(self):
        self.db = conn.get_db()

    def create_student(self, name: str, roll_no: str, email: str, user_id: int):
        try:
            student = StudentModel(name=name, roll_no=roll_no, email=email, user_id=user_id)
            with self.db.begin() as transaction:
                self.db.add(student)
                self.db.commit()
                self.db.refresh(student)
        except exc.IntegrityError as error:
            logging.error(error)
            raise DuplicateError("Similar Record already exists!")
        except Exception as error:
            logging.error(error)
            raise DatabaseError("DB operation Failed: Create_Student")
        return student

    def get_student_by_id(self, student_id: int):
        try:
            student = self.db.query(StudentModel).filter(StudentModel.id == student_id).first()
            if student is None:
                raise NotFoundError("Student does not exist!")
        except Exception as error:
            logging.error(error)
            raise DatabaseError("DB operation Failed: Get_Student_By_Id")
        return student

    def get_students_by_user_id(self, user_id: int):
        try:
            students = self.db.query(StudentModel).filter(StudentModel.user_id == user_id).all()
        except Exception as error:
            logging.error(error)
            raise DatabaseError("DB operation Failed: Get_Students_By_User_Id")
        return students

    def delete_student(self, student_id: int):
        try:
            with self.db.begin() as transaction:
                student = self.db.query(StudentModel).filter(StudentModel.id == student_id).first()
                if student is None:
                    raise NotFoundError("Student does not exist!")
                self.db.query(AnswerModel).filter(AnswerModel.student_id == student.id).delete()
                self.db.delete(student)
                transaction.commit()
        except NotFoundError as error:
            raise error
        except Exception as error:
            logging.error(error)
            self.db.rollback()  # Roll back the transaction explicitly
            raise DatabaseError("DB operation Failed: Delete_Student")
        return True
