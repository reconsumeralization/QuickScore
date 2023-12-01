import datetime

from backend.utils.errors import BadRequestError, InternalServerError, NotFoundError, AuthenticationError
from backend.dao.answer_dao import AnswerDao
from backend.dao.exam_dao import ExamDao
from backend.schemas.answer_schema import AnswerResponse, CreateAnswer, AnswerIndividualResponse
from backend.config.config import config
from backend.rag_models.question_splitter import QuestionSplitter
from backend.rag_models.grader import GraderCohere


class AnswerCore:

    def __init__(self):
        self.answer_dao = AnswerDao()
        self.exam_dao = ExamDao()

    def create_answer(self, input: CreateAnswer, answer_pdf, filename):
        """
        Create an answer and store it in the database.

        Args:
            input (CreateAnswer): The input data for creating the answer.
            answer_pdf: The PDF content of the answer.
            filename: The name of the file.

        Returns:
            Dict: The created answer in JSON format.
        """
        exam_details, context_key = self._get_exam_details(input.exam_id)
        json_answer_pdf = self._parse_answer_pdf(answer_pdf)
        sorted_student_answer = self._sort_json_by_no(json_answer_pdf)
        json_answer_list = self._merge_student_and_answer_key(sorted_student_answer, exam_details["answer_key"])
        evaluation_result, total_score = self._grade_answer(context_key, json_answer_list)

        # Calculate the score and confidence
        score = total_score
        confidence = 0.0

        # Insert the result
        answer_result = self.answer_dao.create_answer(
            exam_id=input.exam_id,
            student_id=input.student_id,
            score=score,
            confidence=confidence,
            evaluation_details=evaluation_result,
            filename=filename
        )
        answer, student = self._extract_answer_and_student(answer_result)
        return self._create_answer_response(answer, student)

    def get_answer_by_id(self, id: int):
        """
        Retrieve an answer by its ID.

        Args:
            id (int): The ID of the answer.

        Returns:
            Dict: The retrieved answer in JSON format.
        """
        answer_result = self.answer_dao.get_answer_by_id(id)
        answer, student = self._extract_answer_and_student(answer_result)
        exam = self.exam_dao.get_exam_by_id(answer["exam_id"])[0].__dict__
        return self._create_individual_answer_response(answer, student, exam)

    def get_answers_by_exam_id(self, exam_id: int):
        """
        Retrieve all answers for a given exam ID.

        Args:
            exam_id (int): The ID of the exam.

        Returns:
            List[Dict]: List of answers in JSON format.
        """
        answers = self.answer_dao.get_answers_by_exam_id(exam_id)
        new_answers = [self._create_answer_response(*self._extract_answer_and_student(answer_result)) for answer_result in answers]
        return [AnswerResponse.model_validate(answer).model_dump(mode="json") for answer in new_answers]

    def delete_answer(self, id: int):
        """
        Delete an answer by its ID.

        Args:
            id (int): The ID of the answer to be deleted.

        Returns:
            bool: True if deletion is successful, False otherwise.
        """
        self.answer_dao.delete_answer(id)
        return True

    def _get_exam_details(self, exam_id: int):
        """
        Get exam details and context key by exam ID.

        Args:
            exam_id (int): The ID of the exam.

        Returns:
            Tuple[Dict, str]: Exam details and context key.
        """
        exam_context_details = self.exam_dao.get_exam_by_id(exam_id)
        if exam_context_details[0] is not None:
            exam_details = exam_context_details[0].__dict__
        else:
            raise InternalServerError("Provided Exam Details not Present")

        if exam_context_details[1] is not None:
            context_details = exam_context_details[1].__dict__
            context_key = context_details["context_key"]
        else:
            context_key = None

        return exam_details, context_key

    def _parse_answer_pdf(self, answer_pdf):
        """
        Parse the answer PDF using QuestionSplitter.

        Args:
            answer_pdf: The PDF content of the answer.

        Returns:
            Dict: The parsed answer in JSON format.
        """
        if answer_pdf == "":
            raise BadRequestError("Could not parse the PDF")
        qs = QuestionSplitter()
        return qs.splitter(answer_pdf)

    def _sort_json_by_no(self, json_data):
        """
        Sort the list of dictionaries by the value of the "no" key.

        Args:
            json_data: The JSON data to be sorted.

        Returns:
            List[Dict]: Sorted list of dictionaries.
        """
        return sorted(json_data, key=lambda x: x['no'])

    def _merge_student_and_answer_key(self, sorted_student_answer, json_answer_key):
        """
        Merge student answers and answer key.

        Args:
            sorted_student_answer: Sorted student answers.
            json_answer_key: Answer key.

        Returns:
            List[Dict]: Merged list of dictionaries.
        """
        j, k = 0, 0
        json_answer_list = []
        for i in range(max(len(sorted_student_answer), len(json_answer_key))):
            temp = {}
            if sorted_student_answer[j]["no"] == json_answer_key[k]["no"]:
                temp["question"] = json_answer_key[k]["question"]
                temp["student_answer"] = sorted_student_answer[j]["answer"]
                temp["answer_key"] = json_answer_key[k]["answer"]
                j += 1
                k += 1
            elif sorted_student_answer[j]["no"] > json_answer_key[k]["no"]:
                temp["question"] = json_answer_key[k]["question"]
                temp["student_answer"] = ""
                temp["answer_key"] = json_answer_key[k]["answer"]
                k += 1
            else:
                raise InternalServerError("Error in Answer key")
            json_answer_list.append(temp)

        return json_answer_list

    def _grade_answer(self, context_key, json_answer_list):
        """
        Grade the answer using GraderCohere.

        Args:
            context_key: Context key.
            json_answer_list: List of merged student answers and answer key.

        Returns:
            Tuple[List[Dict], float]: Evaluation result and total score.
        """
        cohere_grader = GraderCohere(context_key)
        return cohere_grader.grade(json_answer_list)

    def _create_answer_response(self, answer, student):
        """
        Create an answer response.

        Args:
            answer: Answer details.
            student: Student details.

        Returns:
            Dict: Answer response in JSON format.
        """
        result = {
            "id": answer["id"],
            "student_name": student["name"],
            "student_roll_no": student["roll_no"],
            "score": answer["score"],
            "confidence": answer["confidence"],
            "file_name": answer["file_name"]
        }
        return result

    def _create_individual_answer_response(self, answer, student, exam):
        """
        Create an individual answer response.

        Args:
            answer: Answer details.
            student: Student details.
            exam: Exam details.

        Returns:
            Dict: Individual answer response in JSON format.
        """
        result = {
            "id": answer["id"],
            "student_name": student["name"],
            "student_roll_no": student["roll_no"],
            "score": answer["score"],
            "confidence": answer["confidence"],
            "file_name": answer["file_name"],
            "evaluation_details": answer["evaluation_details"],
            "max_exam_score": exam["total_marks"]
        }
        return result

    def _extract_answer_and_student(self, input):
        """
        Extract answer and student details.

        Args:
            input: Input data.

        Returns:
            Tuple[Dict, Dict]: Answer and student details.
        """
        student = input[0].__dict__
        answer = input[1].__dict__
        return answer, student
