import io
import streamlit as st
from datetime import datetime
import frontend.redirect as rd
import pandas as pd
import pdfplumber
from frontend.css.input import input_css
from frontend.side_bar import render_side_bar
from backend.core.exam_core import ExamCore
from backend.core.context_core import ContextCore

REFERENCES_LIST = ["No students to display"]  

def create_exams():
    input_css()
    populate_table()
    render_side_bar()
    st.title("Exams")

    # # Button to show the overlay
    # if custom_button("Upload Exam Details!", "btn1", "background-color: blue; color: white; border-radius: 5px; border: none; padding: 10px 20px;"):
    #     st.session_state.show_overlay = True

    # The overlay layout
    context_dict = get_references_details()
    REFERENCES_LIST = list(context_dict.keys())
    with st.expander("Upload Exam Details"):
        with st.container():
            with st.form(key='exam_details_form'):
                name = st.text_input('Name', key='name')
                conducted_date = str(
                    st.date_input(
                        'Date', value=datetime.now(), key='conducted_date'
                    )
                )
                description = st.text_input('Description', key='description')
                total_marks = st.number_input('Total Score', key='total_marks')
                selected_reference = st.selectbox('Select Reference', REFERENCES_LIST, key='references_name')

                uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=False, key='file_uploader')
                if selected_reference is not None:
                    context_id = context_dict[selected_reference]
                else:
                    context_id = None

                if submitted := st.form_submit_button('Submit'):
                    json_data = {
                        "name": name,
                        "conducted_date": conducted_date,
                        "description": description,
                        "total_marks": total_marks,
                        "user_id": st.session_state.user_id,
                        "context_id": context_id
                    }

                    add_exam(json_data, uploaded_files)

    # Display the table of exam details with 'Edit', 'View', and 'Delete' buttons
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

            if view_button := cols[6].button('👁️', key=f"view_{i}"):
                st.session_state.exam_id = exam_id
                # create_evaluations(exam_id)
                rd.go_to_evaluations()

            # Edit button (you'll need to implement what 'Edit' should do)
            edit_button = cols[7].button('✏️', key=f"edit_{i}")
            if delete_button := cols[8].button('🗑️', key=f"delete_{i}"):
                remove_exam(exam_id)
                st.experimental_rerun()

def populate_table():
    user_id = st.session_state["user_id"]
    exam_core = ExamCore()
    try:
        exams = exam_core.get_exams_by_user_id(user_id)
    except Exception as error:

        st.error("Could not populate the exam data!")

    if len(exams) > 0:
        modified_exams = []
        for key, exam in enumerate(exams):
            item = {
                    'id': exam["id"],
                    'S.No': key+1,
                    'Name': exam["name"],
                    'Date': exam["conducted_date"],
                    'Description': exam["description"],
                    'Total Score': exam["total_marks"],
                    'Files': exam["file_name"]
                    }
            modified_exams.append(item)
        st.session_state.exam_details = modified_exams

def get_references_details():
    user_id = st.session_state["user_id"]
    context_core = ContextCore()
    try:
        contexts = context_core.get_contexts_by_user_id(user_id)
    except Exception as error:
        st.error("Could not fetch the references!")

    return {context['name']: context['id'] for context in contexts}
 
def remove_exam(delete_id):       
    exam_core = ExamCore()
    try:
        exam_core.delete_exam(delete_id)      
    except Exception as error:
        st.error("Delete Operation Failed")
    st.experimental_rerun()
    
    
def add_exam(json_data, file_upload):
    exam_core = ExamCore()
    with st.spinner("Uploading exam details..."):
        try:
            with pdfplumber.open(io.BytesIO(file_upload.getvalue())) as pdf:
                pdf_text = "".join(page.extract_text() for page in pdf.pages)
            exam = exam_core.create_exam(input=json_data, answer_key=pdf_text, filename=file_upload.name)
        except Exception as error:
            print(error)
            st.error("Failed to add exam.")
    
    