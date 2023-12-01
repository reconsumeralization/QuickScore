import streamlit as st
from frontend.chat import render_page
import requests
from frontend.side_bar import render_side_bar
from backend.core.answer_core import AnswerCore

HOST_NAME = "http://localhost:8000"

def get_evaluation_details(_id):
    
    answer_core = AnswerCore()
    answer_result = answer_core.get_answer_by_id(_id)
    print(answer_result)
    return answer_result

def display_info(data):
    markdown_template = f"""
    <style>
        .text-box {{
            border: 1px solid #999;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            background-color: #f0f0f0;
        }}
    </style>
    <style>
        .scrollable-container {{
            height: 210px; /* Fixed height */
            overflow-y: scroll; /* Make it scrollable */
            border: 1px solid #ccc; /* Optional border */
            padding: 10px;
            margin-bottom: 20px; /* Space between containers */
        }}
    </style>
    <h3 style='text-align: center;'> Answer Set </h3>
    <div class="text-box scrollable-container">
        <div style="font-family: sans-serif;">
            <h6 style="color: #4F8BF9;">Question</h2>
            <p style="color: #000;">{data["question"]}</p>
            <h6 style="color: #4F8BF9;">Student Answer</h2>
            <p style="color: #000;">{data["student_answer"]}</p>
        </div>
    </div>
    """
    st.markdown(markdown_template, unsafe_allow_html=True)

# Main layout
def create_individual_evaluation_page():

    # Sample data for the carousel
    carousel_items = [] 
        # Initialize session state variables if they don't exist
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0  # Starting index

    # Function to handle carousel movement
    def next_item():
        st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(carousel_items)

    def prev_item():
        st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(carousel_items)
    
    render_side_bar()   
        
    evaluation_id = st.session_state.evaluation_id
    evaluation_data = get_evaluation_details(evaluation_id)
    carousel_items = evaluation_data["evaluation_details"]
    student_name = evaluation_data["student_name"]
    student_roll = evaluation_data["student_roll_no"]
    total_marks = evaluation_data["max_exam_score"]
    total_student_marks = evaluation_data["score"]

    # Layout for carousel controls
    col1, col2, col3 = st.columns([2, 10, 2])

    # Previous Button
    with col1:
        prev_button = st.button("Previous", on_click=prev_item)
        st.write("\n")
        markdown_template1 = f"""
            <div style="font-family: sans-serif;  padding: 10px; border-radius: 10px; border: 1px solid #cccccc; margin: 10px 0;">
                <h6 style="color: #f8bc64; font-size: 16px;">Student Details</h6>
                <p style="font-size: 14px;"><strong>Name:</strong>
                <br style="line-height:0.5px;" />
                <span>{student_name}</span>
                <br style="line-height:0.5px;" />
                <br style="line-height:0.5px;" />
                <strong>Roll No:</strong>
                <br style="line-height:0.5px;" />
                <span>{student_roll}</span>
                </p>
            </div>
        """

        st.markdown(markdown_template1, unsafe_allow_html=True)

    # Carousel text
    with col2:
        display_info(carousel_items[st.session_state.carousel_index])
        # st.write(carousel_items[st.session_state.carousel_index], anchor='center')

    # Next Button
    with col3:
        next_button = st.button("Next    ", on_click=next_item)
        score = carousel_items[st.session_state.carousel_index]["marks"]
        total_question_marks = 5
        st.write("\n")
        markdown_template1 = f"""
            <div style="font-family: sans-serif;  padding: 10px; border-radius: 10px; border: 1px solid #cccccc; margin: 10px 0;">
                <h6 style="color: #f8bc64; font-size: 16px;">Scoring</h6>
                <p style="font-size: 14px;">Qust. Score:
                <br style="line-height:0.5px;" />
                <span><strong>{score}/{total_question_marks}</strong></span>
                <br style="line-height:0.5px;" />
                <br style="line-height:0.5px;" />
                Exam Score:
                <br style="line-height:0.5px;" />
                <span><strong>{total_student_marks}/{total_marks}</strong></span>
                </p>
            </div>
        """
        st.markdown(markdown_template1, unsafe_allow_html=True)
        

    render_page(evaluation_data)
    
