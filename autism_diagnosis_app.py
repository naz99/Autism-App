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
    # Load custom CSS from a local file
    with open('styles.css') as f:
        custom_css = f.read()
    
    # Add custom CSS to the Streamlit app
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

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
            server.login(EMAIL_USER, EMAIL_PASS)  # Use environment variables for credentials
            msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
            msg['Subject'] = 'Contact Us Form Submission'
            msg['From'] = EMAIL_USER  # Sender's email
            msg['To'] = EMAIL_USER  # Change this to the recipient's email address as a string
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
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
            pdf.cell(200, 10, txt=str(detail), ln=True)

        pdf_file_path = "diagnosis_result.pdf"
        pdf.output(pdf_file_path)

        return pdf_file_path

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

    # Home Section
    if selected == "Home":
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

    # Signup Section
    elif selected == "Signup":
        st.title(":iphone: :blue[Create New Account]")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Signup"):
            add_userdata(conn, new_user, make_hashes(new_password))

    # Login Section
    elif selected == "Login":
        st.title(":calling: :blue[Login Section]")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn, username, hashed_pswd)
            if result:
                st.success(f"Logged In as {username}")
                st.session_state['logged_in'] = True  # Set session state for logged-in users
                st.session_state['username'] = username  # Store the username
                
                # Add button to go to Autism Diagnosis
                if st.button("Go to Autism Diagnosis"):
                    st.session_state['go_to_diagnosis'] = True
                    # Use query parameters to trigger a change in the URL to refresh the app state
                    st.experimental_set_query_params(diagnosis=True)
            else:
                st.warning("Incorrect Username/Password")

    # Autism Diagnosis Section
    elif selected == "Autism Diagnosis" and (st.session_state['logged_in'] or st.session_state.get('go_to_diagnosis', False)):
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
        gender = st.selectbox("Gender", ["Male", "Female"])

        # Prepare input for prediction
        features = [[social_responsiveness, age, int(speech_delay == "Yes"), int(learning_disorder == "Yes"),
                     int(genetic_disorders == "Yes"), int(depression == "Yes"), int(intellectual_disability == "Yes"),
                     int(social_behavioral_issues == "Yes"), int(anxiety_disorder == "Yes"), int(gender == "Male")]]

        if st.button("Predict"):
            # Scale input
            features_scaled = scaler.transform(features)
            prediction = classifier.predict(features_scaled)

            # Output prediction
            diagnosis = "Likely Autism" if prediction[0] == 1 else "Not Likely Autism"
            st.success(f"The prediction is: **{diagnosis}**")

            # Generate PDF report
            if st.button("Generate PDF Report"):
                pdf_path = generate_pdf_result(diagnosis, features)
                st.success(f"PDF report generated: [Download here]({pdf_path})")

    # Contact Us Section
    elif selected == "Contact Us":
        st.title(":envelope: :blue[Contact Us]")
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")
        if st.button("Send"):
            send_email(name, email, message)

    # Logout section
    if selected == "Logout":
        st.session_state['logged_in'] = False
        st.session_state.pop('username', None)  # Clear username from session state
        st.success("You have been logged out.")

    # Close database connection
    conn.close()

if __name__ == "__main__":
    main()
