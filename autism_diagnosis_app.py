import os
import pickle
import sqlite3
import hashlib
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

def main():
    # Set page config at the very start of the main function
    st.set_page_config(page_title="Autism Spectrum Disorder", page_icon=":tada:", layout="wide")

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

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

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
            server.login(EMAIL_USER, EMAIL_PASS)  # Use environment variables for credentials
            msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
            msg['Subject'] = 'Contact Us Form Submission'
            msg['From'] = EMAIL_USER  # Sender's email
            msg['To'] = EMAIL_USER  # Change this to the recipient's email address as a string
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
            server.quit()
            st.success("Your message has been sent successfully!")
        except Exception as e:
            st.error(f"Error sending email: {e}")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    if st.session_state['logged_in']:
        st.sidebar.subheader("Logged in as: " + st.session_state['username'])
        choice = st.sidebar.selectbox("Select an option", ["Home", "Autism Diagnosis", "Contact Us"])
    else:
        choice = st.sidebar.selectbox("Select an option", ["Home", "Login", "Register"])

    if choice == "Home":
        st.title("Welcome to Autism Spectrum Disorder App")
        st.write("This app helps in autism diagnosis and provides information about autism.")
        
    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            conn = init_db_connection()
            if conn:
                create_usertable(conn)
                user = login_user(conn, username, make_hashes(password))
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.success("Login successful!")
                    st.experimental_rerun()  # Refresh the app to show the updated menu
                else:
                    st.error("Invalid username or password")
            conn.close()

    elif choice == "Register":
        st.subheader("Register")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Register"):
            conn = init_db_connection()
            if conn:
                create_usertable(conn)
                add_userdata(conn, new_username, make_hashes(new_password))
                conn.close()
        
    elif choice == "Autism Diagnosis":
        st.subheader("Autism Diagnosis")
        # Add your diagnosis logic here
        st.write("This is where the autism diagnosis logic will go.")
        
    elif choice == "Contact Us":
        st.subheader("Contact Us")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        if st.button("Send"):
            send_email(name, email, message)

if __name__ == '__main__':
    main()
