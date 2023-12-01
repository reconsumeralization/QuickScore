import streamlit as st
from frontend import redirect as rd
from frontend import students
from frontend import exams
from frontend import evaluations
from frontend import teacher_system as teacher_system  # Updated import
from frontend import individual
from frontend import login

# Constants
APP_NAME = "Teacher by WebDUH"  # Updated app name with branding
PAGE_TITLE = "Teacher"  # Updated app name

# Page configuration
st.set_page_config(page_title=PAGE_TITLE, layout="wide")

# Initialize session state variables
st.session_state.setdefault('page', 'home')
st.session_state.setdefault('uploaded_files', [])
st.session_state.setdefault('exam_details', [])
st.session_state.setdefault('show_overlay', False)

# Custom button
def custom_button(text, on_click=None, key=None):
    """
    Function to create a custom button with specific style.
    """
    button_style = """
        <style>
            div.stButton > button:first-child {
                background-color: #0095ee;
                color: white;
                height: 3em;
                border-radius: 5px;
                border: none;
                font-size: 20px;
                font-weight: bold;
                margin: 0.25em;
            }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    return st.button(text, on_click=on_click, key=key)

def set_global_page_config():
    """
    Function to set global page configuration.
    """
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")

def create_homepage():
    """
    Function to create the homepage of the application.
    """
    with st.container():
        st.title(APP_NAME)  # Updated app name with branding
        st.write("Efficiently grade and provide feedback on student answer papers")
        if custom_button("Login", on_click=rd.go_to_login, key="custom_login"):
            pass

        st.write("---")

        st.header("Streamline Your Grading Process")
        st.write(
            "With our website, you can easily grade answer papers and provide comprehensive feedback to students. Save time and effort while ensuring accurate grading."
        )

        st.write("---")

        # FAQ section
        st.subheader("FAQ")
        st.write("Common questions")

        # You can use st.expander to create dropdowns for each FAQ
        faq1 = st.expander("How does Teacher by WebDUH grade the answer paper?")
        faq1.write("The website uses an algorithm to analyze the content of the answer paper and assign a grade based on predefined criteria.")

        faq2 = st.expander("What factors are considered when grading the paper?")
        faq2.write("Teacher by WebDUH considers factors such as accuracy, clarity, organization, and use of supporting evidence when grading the paper.")

        faq3 = st.expander("Can Teacher by WebDUH provide feedback on specific areas for improvement?")
        faq3.write("Yes, Teacher by WebDUH provides detailed feedback on areas where the student can improve their answer, including suggestions for further research or examples to support their arguments.")

        faq4 = st.expander("Is the grading process automated or manual?")
        faq4.write("The grading process is automated, but it is designed to mimic the evaluation process of a human grader as closely as possible.")

        faq5 = st.expander("How often is Teacher by WebDUH updated?")
        faq5.write("Teacher by WebDUH is regularly updated to enhance features, improve performance, and address any issues. Updates are rolled out to ensure a seamless experience for users.")

        faq6 = st.expander("What types of files does Teacher by WebDUH support for uploading?")
        faq6.write("Teacher by WebDUH supports various file formats, including PDFs, images, and text documents. Ensure your files meet the specified requirements for optimal performance.")

        faq7 = st.expander("Can I customize the grading criteria?")
        faq7.write("Yes, Teacher by WebDUH allows users to customize grading criteria based on their preferences and specific requirements. This flexibility ensures adaptability to various grading scenarios.")

        faq8 = st.expander("Are there any restrictions on the file size for uploads?")
        faq8.write("While Teacher by WebDUH can handle large files, there may be practical limitations. It is recommended to check the file size limits and optimize file sizes for a smoother experience.")

        faq9 = st.expander("Is there a limit to the number of users who can access Teacher by WebDUH simultaneously?")
        faq9.write("Teacher by WebDUH is designed to scale based on demand. However, optimal performance is ensured by considering the recommended user load. Contact support for information on handling large user volumes.")

# Main app logic
if st.session_state["page"] == "login":
    login.login_page()
elif st.session_state["page"] == "signup":
    login.signup_page()
elif st.session_state["page"] == "home":
    set_global_page_config()
    create_homepage()
elif st.session_state["page"] == "students":
    students.create_students()
elif st.session_state["page"] == "exams":
    exams.create_exams()
elif st.session_state["page"] == "evaluations":
    evaluations.create_evaluations()
elif st.session_state["page"] == "teacher_system":  # Updated page name
    teacher_system.create_references()  # Updated function call
elif st.session_state["page"] == "individual":
    individual.create_individual_evaluation_page()
