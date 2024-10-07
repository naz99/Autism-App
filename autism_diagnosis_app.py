import streamlit as st
import sqlite3
import hashlib
import time
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pickle
from PIL import Image

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

# Main application function
def main():
    st.set_page_config(page_title="Autism Spectrum Disorder", page_icon=":tada:", layout="wide")

    # Sidebar navigation
    menu = ["Home", "Signup", "Login", "Autism Diagnosis", "Contact Us"]
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

        # Additional home content...

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
            prog = st.progress(0)
            for per_comp in range(100):
                time.sleep(0.05)
                prog.progress(per_comp + 1)
            if result:
                st.success("Logged In as {}".format(username))
                st.warning("Go to Home Menu!")
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
                st.write('The person is not diagnosed with Autism Spectrum Disorder.')
            else:
                st.write('The person is diagnosed with Autism Spectrum Disorder.')

    elif selected == "Contact Us":
        # Contact Us Section
        st.title(":mailbox: :blue[Get In Touch With Us!]")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email", type="email")
        message = st.text_area("Your Message")

if st.button("Send"):
    if name and email and message:
        # Here you would typically handle the form submission, e.g., sending an email
        st.success("Your message has been sent successfully!")
    else:
        st.error("Please fill out all fields.")


        # Load local CSS file for styling
        def local_css(file_name):
            with open(file_name) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        local_css("style.css")  # Ensure 'style.css' is present in your project directory

# Run the main function
if __name__ == '__main__':
    main()
