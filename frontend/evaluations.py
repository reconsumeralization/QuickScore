# Importing necessary modules
from backend.core.student_core import StudentCore
from frontend.side_bar import render_side_bar
from backend.core.answer_core import AnswerCore
import pdfplumber
import streamlit as st
import pandas as pd
import io

# Constants
HOST_NAME = "http://localhost:8000"
TEACHER_NAME = "Webduh"
STUDENTS_LIST = ["No students to display"]

# Main function to create and display the Evaluations page
def create_evaluations():
    st.set_page_config(page_title="Teacher Evaluations - Webduh", page_icon="📚")  # Adding a page title and icon
    st.session_state.evaluation_details = populate_evaluation_table()
    render_side_bar()

    st.title("Evaluations - Teacher: Webduh")  # Added teacher's name for branding

    # Initializing session state variables if not present
    st.session_state.setdefault('evaluation_details', [])
    st.session_state.setdefault('show_overlay', False)

    # Expander to upload evaluation details
    with st.expander("Upload Evaluation Details"):
        student_dict = get_student_details()
        STUDENTS_LIST = list(student_dict.keys())

        # Form to select student and upload file
        with st.form(key='evaluation_details_form'):
            selected_student = st.selectbox('Select Student', STUDENTS_LIST, key='student_name')
            uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False, key='uploaded_file_eval')

            # Improved layout for file uploader and submit button
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(" ")
                st.image("upload_icon.png", caption="", use_column_width=True)  # Add an upload icon
            with col2:
                submitted = st.form_submit_button('Submit')

            # Adding evaluation details on submission
            if submitted and uploaded_file is not None:
                json_data = {'exam_id': st.session_state.exam_id, 'student_id': student_dict[selected_student]}
                add_evaluation(json_data, uploaded_file)
                st.session_state.show_overlay = False
                st.experimental_rerun()

    # Displaying evaluation details if available
    if st.session_state.evaluation_details:
        st.markdown("<br>", unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.evaluation_details)
        display_evaluation_table(df)

# Function to populate the evaluation table with data
def populate_evaluation_table():
    exam_id = st.session_state.exam_id
    answer_core = AnswerCore()
    answer_result = answer_core.get_answers_by_exam_id(exam_id)

    modified_answers = []

    if len(answer_result) > 0:
        for key, answer in enumerate(answer_result):
            item = {
                'id': answer["id"],
                'SNo': key + 1,
                'Name': answer["student_name"],
                'Roll No': answer["student_roll_no"],
                'Score': answer["score"],
                'Status': "completed",
                'File Name': answer["file_name"]
            }
            modified_answers.append(item)

    return modified_answers

# Function to retrieve student details
def get_student_details():
    user_id = st.session_state.user_id
    student_core = StudentCore()

    try:
        student_result = student_core.get_students_by_user_id(user_id=user_id)
    except Exception as error:
        st.error("Could not retrieve student details")

    student_dictionary = {f"{student['name']} ({student['roll_no']}": student['id'] for student in student_result}
    return student_dictionary

# Function to remove an evaluation
def remove_evaluation(delete_id):
    answer_core = AnswerCore()

    try:
        answer_core.delete_answer(delete_id)
        st.success("Successfully removed the evaluation!!")
        st.experimental_rerun()
    except Exception as error:
        print(error)
        st.error("Cannot remove evaluation. Please try again.")

# Function to add evaluation details
def add_evaluation(json_data, file_upload):
    filename = file_upload.name
    answer_core = AnswerCore()
    pdf_data = file_upload.read()

    with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
        answer_pdf = "".join(page.extract_text() for page in pdf.pages)

    with st.spinner("Uploading evaluation details..."):
        answer_core.create_answer(input=json_data, answer_pdf=pdf_data, filename=filename)
        st.success("Answer added successfully.")
        st.experimental_rerun()

# Function to display the evaluation table
def display_evaluation_table(df):
    st.markdown("<br>", unsafe_allow_html=True)

    col_headers = st.columns((1, 1, 1, 1, 1, 1, 0.5, 0.5))
    headers = ["SNo", "Name", "Roll No", "Score", "Status", "File Name", "View", "Delete"]

    # Improved styling for table headers
    for col_header, header in zip(col_headers, headers):
        col_header.markdown(f'<h5 style="color: #4F8BF9;"><strong>{header}</strong></h5></div>', unsafe_allow_html=True)

    for i, row in df.iterrows():
        cols = st.columns((1, 1, 1, 1, 1, 1, 0.5, 0.5))
        cols[0].write(str(i + 1))
        cols[1].write(row['Name'])
        cols[2].write(row['Roll No'])
        cols[3].write(str(row['Score']))
        cols[4].write(row['Status'])
        cols[5].write(row['File Name'])

        # Improved styling for view and delete buttons
        view_button = cols[6].button('👁️ View', key=f"view_{i}")
        if view_button:
            view_evaluation(row['id'])

        delete_button = cols[7].button('🗑️ Delete', key=f"delete_{i}")
        if delete_button:
            remove_evaluation(row['id'])
            del st.session_state.evaluation_details[i]
            st.experimental_rerun()

# Function to view an individual evaluation
def view_evaluation(_id):
    st.session_state.evaluation_id = _id
    rd.go_to_individual_evaluation()  # Assuming rd is defined somewhere in the code.
