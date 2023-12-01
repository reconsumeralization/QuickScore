from typing import Dict, List, Tuple

from backend.utils.errors import BadRequestError, InternalServerError
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

    def create_answer(self, create_answer: CreateAnswer, answer_pdf: str, filename: str) -> Dict:
        """
        Create an answer based on the provided details.

        Args:
            create_answer (CreateAnswer): The details of the answer to be created.
            answer_pdf (str): The PDF containing the answers.
            filename (str): The name of the file.

        Returns:
            Dict: The created answer response.
        """
        exam_details, context_key = self.get_exam_details(create_answer.exam_id)
        json_answer_list = self.process_answer_pdf(answer_pdf, exam_details["answer_key"])
        evaluation_result, total_score = self.grade_answer(context_key, json_answer_list)

        answer_result = self.answer_dao.create_answer(
            exam_id=create_answer.exam_id,
            student_id=create_answer.student_id,
            score=total_score,
            confidence=0.0,
            evaluation_details=evaluation_result,
            filename=filename
        )
        answer, student = self.extract_answer_and_student(answer_result)
        return self.create_answer_response(answer, student)

    def process_answer_pdf(self, answer_pdf: str, answer_key: List[Dict]) -> List[Dict]:
        """
        Process the answer PDF to extract relevant information.

        Args:
            answer_pdf (str): The PDF containing the answers.
            answer_key (List[Dict]): The answer key.

        Returns:
            List[Dict]: Processed information from the answer PDF.
        """
        if not answer_pdf:
            raise BadRequestError("Could not parse the PDF")

        qs = QuestionSplitter()
        sorted_student_answer = sorted(qs.splitter(answer_pdf), key=lambda x: x['no'])
        return self.merge_student_and_answer_key(sorted_student_answer, answer_key)

    def get_answer_by_id(self, answer_id: int) -> Dict:
        """
        Retrieve an answer based on its ID.

        Args:
            answer_id (int): The ID of the answer.

        Returns:
            Dict: The individual answer response.
        """
        answer, student, exam = self.get_individual_answer_details(answer_id)
        return self.create_individual_answer_response(answer, student, exam)

    def get_answers_by_exam_id(self, exam_id: int) -> List[Dict]:
        """
        Retrieve answers for a specific exam.

        Args:
            exam_id (int): The ID of the exam.

        Returns:
            List[Dict]: The list of answer responses.
        """
        answers = self.answer_dao.get_answers_by_exam_id(exam_id)
        return [self.create_answer_response(*self.extract_answer_and_student(answer_result)) for answer_result in answers]

    def delete_answer(self, answer_id: int) -> bool:
        """
        Delete an answer based on its ID.

        Args:
            answer_id (int): The ID of the answer.

        Returns:
            bool: True if deletion is successful.
        """
        self.answer_dao.delete_answer(answer_id)
        return True

    def get_exam_details(self, exam_id: int) -> Tuple[Dict, str]:
        """
        Retrieve details of an exam.

        Args:
            exam_id (int): The ID of the exam.

        Returns:
            Tuple[Dict, str]: Exam details and context key.
        """
        exam_context_details = self.exam_dao.get_exam_by_id(exam_id)
        exam_details = exam_context_details[0].__dict__ if exam_context_details[0] else {}
        context_key = exam_context_details[1].__dict__["context_key"] if exam_context_details[1] else None

        if not exam_details:
            raise InternalServerError("Provided Exam Details not Present")

        return exam_details, context_key

    def merge_student_and_answer_key(self, sorted_student_answer: List[Dict], json_answer_key: List[Dict]) -> List[Dict]:
        """
        Merge student answers with the answer key.

        Args:
            sorted_student_answer (List[Dict]): Sorted list of student answers.
            json_answer_key (List[Dict]): Answer key.

        Returns:
            List[Dict]: Merged list of student answers and answer key.
        """
        json_answer_list = []
        j, k = 0, 0

        while j < len(sorted_student_answer) or k < len(json_answer_key):
            temp = {}

            if (
                j < len(sorted_student_answer)
                and k < len(json_answer_key)
                and sorted_student_answer[j]["no"] == json_answer_key[k]["no"]
            ):
                temp["question"] = json_answer_key[k]["question"]
                temp["student_answer"] = sorted_student_answer[j]["answer"]
                temp["answer_key"] = json_answer_key[k]["answer"]
                j += 1
                k += 1
            elif k < len(json_answer_key) and (
                j == len(sorted_student_answer) or sorted_student_answer[j]["no"] > json_answer_key[k]["no"]
            ):
                temp["question"] = json_answer_key[k]["question"]
                temp["student_answer"] = ""
                temp["answer_key"] = json_answer_key[k]["answer"]
                k += 1
            else:
                raise InternalServerError("Error in Answer key")

            json_answer_list.append(temp)

        return json_answer_list

    def grade_answer(self, context_key: str, json_answer_list: List[Dict]) -> Tuple[List[Dict], float]:
        """
        Grade answers using the provided context key.

        Args:
            context_key (str): The context key.
            json_answer_list (List[Dict]): List of student answers.

        Returns:
            Tuple[List[Dict], float]: Evaluation details and total score.
        """
        cohere_grader = GraderCohere(context_key)
        return cohere_grader.grade(json_answer_list)

    def create_answer_response(self, answer: Dict, student: Dict) -> Dict:
        """
        Create a response for an answer.

        Args:
            answer (Dict): Answer details.
            student (Dict): Student details.

        Returns:
            Dict: Answer response.
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

    def get_individual_answer_details(self, answer_id: int) -> Tuple[Dict, Dict, Dict]:
        """
        Retrieve details of an individual answer.

        Args:
            answer_id (int): The ID of the answer.

        Returns:
            Tuple[Dict, Dict, Dict]: Answer, student, and exam details.
        """
        answer_result = self.answer_dao.get_answer_by_id(answer_id)
        answer, student = self.extract_answer_and_student(answer_result)
        exam = self.exam_dao.get_exam_by_id(answer["exam_id"])[0].__dict__
        return answer, student, exam

    def create_individual_answer_response(self, answer: Dict, student: Dict, exam: Dict) -> Dict:
        """
        Create a response for an individual answer.

        Args:
            answer (Dict): Answer details.
            student (Dict): Student details.
            exam (Dict): Exam details.

        Returns:
            Dict: Individual answer response.
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

    def extract_answer_and_student(self, input: Tuple) -> Tuple[Dict, Dict]:
        """
        Extract answer and student details from input tuple.

        Args:
            input (Tuple): Tuple containing student and answer details.

        Returns:
            Tuple[Dict, Dict]: Extracted answer and student details.
        """
        student, answer = input[0].__dict__, input[1].__dict__
        return answer, student
