import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import pickle
import base64
from fpdf import FPDF  # Import the fpdf library for PDF generation
import smtplib
from email.mime.text import MIMEText

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
        server.login("nazruliskandar99.ni@gmail.com", "ompo rqui qgxb fzyl")
        msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
        msg['Subject'] = 'Contact Us Form Submission'
        msg['From'] = email
        msg['To'] = "nazruliskandar99.ni@gmail.com"
        server.sendmail(email, "nazruliskandar99.ni@gmail.com", msg.as_string())
        server.quit()
        st.success("Your message has been sent successfully!")
    except Exception as e:
        st.error(f"An error occurred while sending the email: {e}")

# Function to generate PDF
def generate_pdf(input_data, prediction_result):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Autism Diagnosis Result", ln=True, align='C')
    pdf.ln(10)  # New line
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "User's Input Data:", ln=True)
    pdf.ln(5)
    data_labels = [
        "Social Responsiveness", "Age", "Speech Delay", "Learning Disorder", 
        "Genetic Disorders", "Depression", "Intellectual Disability",
        "Social/Behavioral Issues", "Anxiety Disorder", "Gender",
        "Suffers from Jaundice", "Family Member History with ASD"
    ]
    for label, value in zip(data_labels, input_data):
        pdf.cell(0, 10, f"{label}: {value}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Diagnosis Result:", ln=True)
    pdf.set_font("Arial", "", 12)
    diagnosis = "Not diagnosed with Autism Spectrum Disorder" if prediction_result == 0 else "Diagnosed with Autism Spectrum Disorder"
    pdf.cell(0, 10, f"The person is {diagnosis}.", ln=True)
    pdf_filename = "autism_diagnosis_result.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

# Function to convert PDF to downloadable link
def get_pdf_download_link(pdf_filename):
    with open(pdf_filename, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{pdf_filename}">Download PDF Result</a>'
    return href

# Main application function
def main():
    st.set_page_config(page_title="Autism Spectrum Disorder", page_icon=":tada:", layout="wide")
    conn = init_db_connection()
    if conn is None:
        st.stop()  # Stop execution if database connection failed
    create_usertable(conn)  # Ensure the table is created at the start

    # Navigation
    page = st.sidebar.radio("Select a page", ["Login", "Signup"])

    if page == "Login":
        # Login Section
        st.title(":blue[Autism Spectrum Disorder]")
        st.write("Welcome to the Autism Spectrum Disorder Diagnosis Application.")
        st.write("Please login to continue.")
        
        # Login Form
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn, username, hashed_pswd)
            if result:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success(f"Logged In as {username}")
                st.experimental_rerun()  # Refresh the app to show the main content
            else:
                st.warning("Incorrect Username/Password")

        # Forgot Password Section
        st.write("### Forgot Password?")
        st.write("If you have forgotten your password, please contact support.")

        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            st.write("Please login or sign up to access the Autism Diagnosis and other sections.")

    elif page == "Signup":
        # Signup Section
        st.title(":blue[Signup Page]")
        st.write("Create a new account below:")
        new_user = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        if st.button("Signup"):
            add_userdata(conn, new_user, make_hashes(new_password))

# Run the application
if __name__ == '__main__':
    main()
