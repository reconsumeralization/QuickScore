# Importing necessary modules
from datetime import datetime
import pandas as pd
import pdfplumber
import streamlit as st

from backend.core.context_core import ContextCore
from backend.core.exam_core import ExamCore
import frontend.redirect as rd
from frontend.css.input import input_css
from frontend.side_bar import render_side_bar


# Constants
REFERENCES_LIST = ["No students to display"]


def get_references_details():
    """Function to get references details"""
    context_core = ContextCore()
    user_id = st.session_state["user_id"]

    try:
        contexts = context_core.get_contexts_by_user_id(user_id)
    except Exception as error:
        st.error("Could not fetch the references!")

    return {context['name']: context['id'] for context in contexts}


def populate_table():
    """Function to populate the table with exam details"""
    exam_core = ExamCore()
    user_id = st.session_state["user_id"]

    try:
        exams = exam_core.get_exams_by_user_id(user_id)
    except Exception as error:
        st.error("Could not populate the exam data!")

    if exams:
        st.session_state.exam_details = [
            {
                'id': exam["id"],
                'S.No': key + 1,
                'Name': exam["name"],
                'Date': exam["conducted_date"],
                'Description': exam["description"],
                'Total Score': exam["total_marks"],
                'Files': exam["file_name"]
            }
            for key, exam in enumerate(exams)
        ]


def remove_exam(delete_id):
    """Function to remove an exam"""
    exam_core = ExamCore()

    try:
        exam_core.delete_exam(delete_id)
    except Exception as error:
        st.error("Delete Operation Failed")

    st.experimental_rerun()


def add_exam(json_data, file_upload):
    """Function to add exam details"""
    exam_core = ExamCore()

    with st.spinner("Uploading exam details..."):
        try:
            with pdfplumber.open(io.BytesIO(file_upload.getvalue())) as pdf:
                pdf_text = "".join(page.extract_text() for page in pdf.pages)

            exam_core.create_exam(input=json_data, answer_key=pdf_text, filename=file_upload.name)
        except Exception as error:
            st.error(f"Failed to add exam.")


def create_exams():
    """Function to create exams"""
    input_css()
    populate_table()
    render_side_bar()
    st.title("Exams")

    context_dict = get_references_details()

    with st.expander("Upload Exam Details"):
        with st.container():
            with st.form(key='exam_details_form'):
                # Input fields
                name = st.text_input('Name', key='name')
                conducted_date = st.date_input('Date', value=datetime.today(), key='conducted_date')
                description = st.text_input('Description', key='description')
                total_marks = st.number_input('Total Score', key='total_marks')
                selected_reference = st.selectbox('Select Reference', list(context_dict.keys()), key='references_name')

                # File uploader
                uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=False, key='file_uploader')

                context_id = context_dict.get(selected_reference)

                submitted = st.form_submit_button('Submit')
                if submitted:
                    json_data = {
                        "name": name,
                        "conducted_date": str(conducted_date),
                        "description": description,
                        "total_marks": total_marks,
                        "user_id": st.session_state.user_id,
                        "context_id": context_id
                    }

                    add_exam(json_data, uploaded_files)

    if st.session_state.exam_details:
        st.markdown("<br>", unsafe_allow_html=True)

        df = pd.DataFrame(st.session_state.exam_details)
        col_headers = st.columns((1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.5))
        headers = ["S.No", "Name", "Date", "Description", "Total Score", "Files", "View", "Edit", "Delete"]

        for col_header, header in zip(col_headers, headers):
            col_header.markdown(f'<h5 style="color: #4F8BF9;"><strong>{header}</strong></h5></div>', unsafe_allow_html=True)

        for i, row in df.iterrows():
            exam_id = row['id']
            cols = st.columns((1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.5))
            cols[0].write(str(i + 1))
            cols[1].write(row['Name'])
            cols[2].write(row['Date'])
            cols[3].write(row['Description'])
            cols[4].write(str(row['Total Score']))
            cols[5].write(row['Files'])

            view_button = cols[6].button('👁️', key=f"view_{i}")
            if view_button:
                st.session_state.exam_id = exam_id
                rd.go_to_evaluations()

            edit_button = cols[7].button('✏️', key=f"edit_{i}")
            if edit_button:
                pass

            delete_button = cols[8].button('🗑️', key=f"delete_{i}")
            if delete_button:
                remove_exam(exam_id)
                st.experimental_rerun()
