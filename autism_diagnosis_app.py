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
import base64

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
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Log in to your email account (use App Password)
        server.login("nazruliskandar99.ni@gmail.com", "ompo rqui qgxb fzyl")  # Replace with your email and app password

        # Create the email content
        msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
        msg['Subject'] = 'Contact Us Form Submission'
        msg['From'] = email
        msg['To'] = "your_email@gmail.com"  # Replace with your email to receive messages

        # Send the email
        server.sendmail(email, "nazruliskandar99.ni@gmail.com", msg.as_string())  # Replace with your email to receive messages
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

    # Title and content
    pdf.cell(200, 10, txt="Autism Diagnosis Result", ln=True, align='C')
    pdf.ln(10)  # New line

    # Add input data to PDF
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

    # Add the prediction result
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Diagnosis Result:", ln=True)
    pdf.set_font("Arial", "", 12)
    diagnosis = "Not diagnosed with Autism Spectrum Disorder" if prediction_result == 0 else "Diagnosed with Autism Spectrum Disorder"
    pdf.cell(0, 10, f"The person is {diagnosis}.", ln=True)

    # Save PDF to a file
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

    # Initialize database connection
    conn = init_db_connection()
    if conn is None:
        st.stop()  # Stop execution if database connection failed

    create_usertable(conn)  # Ensure the table is created at the start

    # First page for Signup/Login
    st.title(":blue[Autism Spectrum Disorder]")
    st.write("Welcome to the Autism Spectrum Disorder Diagnosis Application.")
    st.write("Please login or create an account to continue.")
    selected_action = st.radio("Choose an action:", ["Signup", "Login"])

    if selected_action == "Signup":
        st.subheader(":iphone: Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Signup"):
            add_userdata(conn, new_user, make_hashes(new_password))

    elif selected_action == "Login":
        st.subheader(":calling: Login Section")
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

    # Navigation for other pages
    menu = ["Home", "Autism Diagnosis", "Review Results", "Contact Us"]
    selected_page = st.sidebar.radio("Navigation", menu)

    if selected_page == "Home":
        st.write("---")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.title("What is Autism Spectrum Disorder?")
            st.write("Autism spectrum disorder (ASD) is a developmental disability caused by differences in the brain. People with ASD often have problems with social communication and interaction, and restricted or repetitive behaviors or interests.")
        with col2:
            img1 = Image.open("asd_child.jpg")
            st.image(img1, width=300)

    elif selected_page == "Autism Diagnosis":
        st.title('Autism Diagnosis')
        classifier, scaler = load_model_and_scaler()
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
            input_data = [
                social_responsiveness, age,
                int(speech_delay == "Yes"), int(learning_disorder == "Yes"),
                int(genetic_disorders == "Yes"), int(depression == "Yes"),
                int(intellectual_disability == "Yes"), int(social_behavioral_issues == "Yes"),
                int(anxiety_disorder == "Yes"), int(gender == "Male"),
                int(suffers_from_jaundice == "Yes"), int(family_member_history_with_asd == "Yes")
            ]

            scaled_data = scaler.transform([input_data])
            prediction = classifier.predict(scaled_data)

            # Display the prediction result
            st.write("### Diagnosis Result")
            if prediction == 0:
                st.write("The person is **not** diagnosed with Autism Spectrum Disorder.")
            else:
                st.write("The person is diagnosed with **Autism Spectrum Disorder**.")

            # Save the input data and prediction in session state
            st.session_state['input_data'] = input_data
            st.session_state['prediction'] = prediction

    elif selected_page == "Review Results":
        st.title("Review Your Previous Diagnosis")

        if 'input_data' in st.session_state and 'prediction' in st.session_state:
            st.write("### Your Input Data")
            st.write(pd.DataFrame([st.session_state['input_data']], columns=[
                "Social Responsiveness", "Age", "Speech Delay", "Learning Disorder", 
                "Genetic Disorders", "Depression", "Intellectual Disability",
                "Social/Behavioral Issues", "Anxiety Disorder", "Gender",
                "Suffers from Jaundice", "Family Member History with ASD"]))

            st.write("### Diagnosis Result")
            if st.session_state['prediction'] == 0:
                st.write("The person is **not** diagnosed with Autism Spectrum Disorder.")
            else:
                st.write("The person is diagnosed with **Autism Spectrum Disorder**.")

            # Generate and download PDF
            if st.button("Save Results as PDF"):
                pdf_filename = generate_pdf(st.session_state['input_data'], st.session_state['prediction'])
                st.success("PDF generated successfully!")

                # Provide download link for the PDF
                pdf_download_link = get_pdf_download_link(pdf_filename)
                st.markdown(pdf_download_link, unsafe_allow_html=True)
        else:
            st.write("No previous diagnosis results found. Please go to the Autism Diagnosis section to conduct a diagnosis.")

    elif selected_page == "Contact Us":
        st.title(":mailbox: :blue[Contact Us]")
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")
        if st.button("Send"):
            send_email(name, email, message)

# Run the application
if __name__ == '__main__':
    main()
