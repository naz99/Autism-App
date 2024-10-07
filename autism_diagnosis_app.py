import streamlit as st
import sqlite3
import hashlib
import time
import pandas as pd
import pickle
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from fpdf import FPDF
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
DATABASE_NAME = 'naz.db'
MODEL_FILE = "autism_random_forest.pkl"
SCALER_FILE = 'scaler.pkl'
DATASET_FILE = "asd_data_csv.csv"

# Function to hash passwords
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Initialize database connection
def init_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except sqlite3.DatabaseError as e:
        st.error(f"Database connection failed: {e}")
        return None

# Create a new table if it doesn't exist
def create_usertable(conn):
    try:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
        conn.commit()
    except sqlite3.DatabaseError as e:
        st.error(f"Error creating table: {e}")

# Add new user data
def add_userdata(conn, username, password):
    try:
        c = conn.cursor()
        c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        st.success(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        st.error(f"Username '{username}' already exists. Please choose a different username.")
    except sqlite3.DatabaseError as e:
        st.error(f"Error adding user data: {e}")

# Verify login details
def login_user(conn, username, password):
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
        return c.fetchall()
    except sqlite3.DatabaseError as e:
        st.error(f"Login error: {e}")
        return []

# Load the model and scaler
@st.cache_resource
def load_model_and_scaler():
    with open(MODEL_FILE, "rb") as model_file:
        classifier = pickle.load(model_file)
    with open(SCALER_FILE, "rb") as scaler_file:
        scaler = pickle.load(scaler_file)
    return classifier, scaler

# Load the dataset
@st.cache_data
def load_data():
    asd_data_csv = pd.read_csv(DATASET_FILE)
    return asd_data_csv

# Send email function
def send_email(name, email, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_APP_PASSWORD"))  # Use environment variables
        msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
        msg['Subject'] = 'Contact Us Form Submission'
        msg['From'] = email
        msg['To'] = os.getenv("nazruliskandar99.ni@gmail.com")  # Replace with your email to receive messages
        server.sendmail(email, os.getenv("nazruliskandar99.ni@gmail.com"), msg.as_string())  # Replace with your email to receive messages
        server.quit()
        st.success("Your message has been sent successfully!")
    except Exception as e:
        st.error(f"An error occurred while sending the email: {e}")

# Function to generate PDF report
def generate_pdf_result(result, details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Autism Diagnosis Result", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Diagnosis: {result}", ln=True)
    
    pdf.cell(200, 10, txt="Details:", ln=True)
    for detail in details:
        pdf.cell(200, 10, txt=detail, ln=True)

    pdf_file_path = "diagnosis_result.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path

# Main application function
def main():
    st.set_page_config(page_title="Autism Spectrum Disorder", page_icon=":tada:", layout="wide")

    # Sidebar navigation
    menu = ["Home", "Signup", "Login", "Contact Us"]
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        menu.append("Autism Diagnosis")
        menu.append("Logout")  # Add logout option to the menu

    selected = st.sidebar.radio("Navigation", menu)

    conn = init_db_connection()
    if conn is None:
        st.stop()  # Stop execution if database connection failed

    create_usertable(conn)  # Ensure the table is created at the start

    if selected == "Home":
        # Home section content
        st.title(":blue[Autism Spectrum Disorder]")
        st.write("---")
        with st.container():
            col1, col2 = st.columns([3, 2])
            with col1:
                st.title("What is Autism Spectrum Disorder?")
                st.write("Autism spectrum disorder (ASD) is a developmental disability caused by differences in the brain. People with ASD often have problems with social communication and interaction, and restricted or repetitive behaviors or interests.")
            with col2:
                img1 = Image.open("asd_child.jpg")
                st.image(img1, width=300)

    elif selected == "Signup":
        # Signup Section
        st.title(":iphone: :blue[Create New Account]")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Signup"):
            add_userdata(conn, new_user, make_hashes(new_password))

    elif selected == "Login":
        # Login Section
        st.title(":calling: :blue[Login Section]")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn, username, hashed_pswd)
            if result:
                st.success("Logged In as {}".format(username))
                st.session_state['logged_in'] = True  # Set session state for logged-in users
                st.session_state['username'] = username  # Store the username
                st.write("Click below to proceed to Autism Diagnosis")
                if st.button("Go to Autism Diagnosis"):
                    st.experimental_rerun()  # Refresh the app to show the Autism Diagnosis section
            else:
                st.warning("Incorrect Username/Password")

    elif selected == "Autism Diagnosis":
        # Autism Diagnosis Section
        st.title('Autism Diagnosis')

        # Load model and scaler
        classifier, scaler = load_model_and_scaler()

        # Input form for prediction
        social_responsiveness = st.slider("Social Responsiveness", min_value=0, max_value=10)
        age = st.slider("Age", min_value=0, max_value=18)
        speech_delay = st.radio("Speech Delay", ["No", "Yes"])
        learning_disorder = st.radio("Learning Disorder", ["No", "Yes"])
        genetic_disorders = st.radio("Genetic Disorders", ["No", "Yes"])
        depression = st.radio("Depression", ["No", "Yes"])
        intellectual_disability = st.radio("Intellectual Disability", ["No", "Yes"])
        social_behavioral_issues = st.radio("Social/Behavioral Issues", ["No", "Yes"])
        anxiety_disorder = st.radio("Anxiety Disorder", ["No", "Yes"])
        gender = st.selectbox("Gender", ["Female", "Male"])
        suffers_from_jaundice = st.radio("Suffers from Jaundice", ["No", "Yes"])
        family_member_history_with_asd = st.radio("Family member history with ASD", ["No", "Yes"])
        submit_button = st.button(label='Predict')

        if submit_button:
            # Convert input data to numerical values
            input_data = [
                social_responsiveness, age,
                1 if speech_delay == "Yes" else 0,
                1 if learning_disorder == "Yes" else 0,
                1 if genetic_disorders == "Yes" else 0,
                1 if depression == "Yes" else 0,
                1 if intellectual_disability == "Yes" else 0,
                1 if social_behavioral_issues == "Yes" else 0,
                1 if anxiety_disorder == "Yes" else 0,
                1 if gender == "Female" else 0,
                1 if suffers_from_jaundice == "Yes" else 0,
                1 if family_member_history_with_asd == "Yes" else 0
            ]

            # Standardize the input data
            input_data_standardized = scaler.transform([input_data])

            # Make prediction
            prediction = classifier.predict(input_data_standardized)

            # Interpretation of prediction
            if prediction[0] == 0:
                result_text = 'The person is not diagnosed with Autism Spectrum Disorder.'
            else:
                result_text = 'The person is diagnosed with Autism Spectrum Disorder.'

            # Store the result for later review
            st.session_state['diagnosis_result'] = result_text
            st.session_state['diagnosis_details'] = input_data

            # Generate PDF report
            pdf_file_path = generate_pdf_result(result_text, input_data)
            st.success("Diagnosis Result: " + result_text)
            st.download_button("Download Diagnosis Report", pdf_file_path, "diagnosis_result.pdf")

    elif selected == "Contact Us":
        # Contact Us section
        st.title("Contact Us")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        if st.button("Send"):
            if name and email and message:
                send_email(name, email, message)
            else:
                st.warning("Please fill in all fields.")

    elif selected == "Logout":
        # Logout functionality
        st.session_state['logged_in'] = False  # Clear logged-in state
        st.session_state.pop('username', None)  # Remove username from session state
        st.success("You have logged out successfully!")
        st.experimental_rerun()  # Refresh the app

    conn.close()

if __name__ == "__main__":
    main()
