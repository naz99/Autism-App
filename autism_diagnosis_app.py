import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import pickle
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from fpdf import FPDF
from dotenv import load_dotenv
import os

# Set page config at the very start of the script
st.set_page_config(page_title="Autism Spectrum Disorder", page_icon=":tada:", layout="wide")

def main():
    # Load environment variables
    load_dotenv()
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    # Check if environment variables are loaded
    if EMAIL_USER is None or EMAIL_PASS is None:
        st.error("Error loading email credentials. Please check your .env file.")

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
            server.login(EMAIL_USER, EMAIL_PASS)
            msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
            msg['Subject'] = 'Contact Us Form Submission'
            msg['From'] = EMAIL_USER
            msg['To'] = EMAIL_USER
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
            server.quit()
            st.success("Your message has been sent successfully!")
        except Exception as e:
            st.error(f"An error occurred while sending the email: {e}")

    # Function to generate PDF report
    def generate_pdf_result(name, diagnosis_result, input_data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Autism Diagnosis Result", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Patient Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Diagnosis: {diagnosis_result}", ln=True)
        pdf.cell(200, 10, txt="Input Data Results:", ln=True)

        labels = [
            "Social Responsiveness",
            "Age",
            "Speech Delay",
            "Learning Disorder",
            "Genetic Disorders",
            "Depression",
            "Intellectual Disability",
            "Social/Behavioral Issues",
            "Anxiety Disorder",
            "Gender (Male=1/Female=0)",
            "Suffers from Jaundice",
            "Family History with ASD"
        ]

        input_data_converted = []
        for i, value in enumerate(input_data[0]):
            if labels[i] != "Gender (Male=1/Female=0)":
                input_data_converted.append("Yes" if value == 1 else "No" if value == 0 else value)
            else:
                input_data_converted.append(value)

        for label, value in zip(labels, input_data_converted):
            pdf.cell(200, 10, txt=f"{label}: {value}", ln=True)

        pdf_file_path = "diagnosis_result.pdf"
        pdf.output(pdf_file_path)
        return pdf_file_path

    # Sidebar navigation
    st.sidebar.title("Navigation")
    menu = ["Home", "Signup", "Login", "Contact Us"]
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        menu.append("Autism Diagnosis")
        menu.append("Logout")

    selected = st.sidebar.selectbox("Select Page", menu)

    conn = init_db_connection()
    if conn is None:
        st.stop()

    create_usertable(conn)

    # Home Section
    if selected == "Home":
        st.title("What is Autism Spectrum Disorder?")
        st.write("Autism spectrum disorder (ASD) is a developmental disability...")
        
        img1 = Image.open("asd_child.jpg")
        st.image(img1, width=300)
        
    # Signup Section
    elif selected == "Signup":
        st.title("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Signup"):
            add_userdata(conn, new_user, make_hashes(new_password))
    
    # Login Section
    elif selected == "Login":
        st.title("Login Section")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn, username, hashed_pswd)
            if result:
                st.success(f"Logged In as {username}")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.warning("Incorrect Username/Password")

    # Autism Diagnosis Section
    elif selected == "Autism Diagnosis" and st.session_state.get('logged_in'):
        st.title('Autism Diagnosis')
        classifier, scaler = load_model_and_scaler()

        social_responsiveness = st.slider("Social Responsiveness", min_value=0, max_value=10)
        age = st.slider("Age", min_value=0, max_value=18)
        speech_delay = st.selectbox("Speech Delay", options=["Yes", "No"])
        
        input_data = [[
            social_responsiveness,
            age,
            1 if speech_delay == "Yes" else 0
        ]]

        input_data_scaled = scaler.transform(input_data)
        diagnosis = classifier.predict(input_data_scaled)

        result = "Positive" if diagnosis[0] == 1 else "Negative"
        st.success(f"Diagnosis Result: {result}")

        pdf_path = generate_pdf_result(st.session_state['username'], result, input_data)
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        st.download_button("Download Diagnosis Report", pdf_data, file_name=pdf_path)

    # Contact Us Section
    elif selected == "Contact Us":
        st.title("Contact Us")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        if st.button("Send"):
            send_email(name, email, message)

    # Logout Section
    elif selected == "Logout":
        st.session_state['logged_in'] = False
        st.success("Logged out successfully.")

    conn.close()

if __name__ == "__main__":
    main()
