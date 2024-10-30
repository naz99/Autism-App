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
    def generate_pdf_result(name, diagnosis_result, input_data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Autism Diagnosis Result", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Patient Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Diagnosis: {diagnosis_result}", ln=True)
        pdf.cell(200, 10, txt="Input Data Results:", ln=True)

        # Add input data with labels and convert 1/0 to Yes/No accordingly
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

        # Convert input_data values, keeping gender unchanged
        input_data_converted = []
        for i, value in enumerate(input_data[0]):  # input_data is in a nested list
            if labels[i] != "Gender (Male=1/Female=0)":
                if value == 1:
                    input_data_converted.append("Yes")
                elif value == 0:
                    input_data_converted.append("No")
                else:
                    input_data_converted.append(value)  # Keep other values (like age) unchanged
            else:
                input_data_converted.append(value)  # Keep gender unchanged

        # Create the PDF rows
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
        menu.append("Logout")  # Add logout option to the menu

    selected = st.sidebar.selectbox("Select Page", menu)  # Sidebar dropdown for navigation

    conn = init_db_connection()
    if conn is None:
        st.stop()  # Stop execution if database connection failed

    create_usertable(conn)  # Ensure the table is created at the start

    # Home Section
    if selected == "Home":

       st.markdown(
        """
        <style>
        .stApp {
            background-color: #C3B1E1;  /* Change this to your desired color */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

        st.write("---")
        with st.container():
            col1, col2 = st.columns([3, 2])
            with col1:
                st.title("What is Autism Spectrum Disorder?")
                st.write("Autism spectrum disorder (ASD) is a developmental disability caused by differences in the brain. People with ASD often have problems with social communication and interaction, and restricted or repetitive behaviors or interests.")

                st.title("What Causes Autism Spectrum Disorder?")
                st.write("The Autism Spectrum Disorder Foundation lists the following as possible causes of ASD:")

                st.markdown("**<mark>Genetics</mark>**: Research suggests that ASD can be caused by a combination of genetic and environmental factors. Some genes have been identified as being associated with an increased risk for ASD, but no single gene has been proven to cause ASD.", unsafe_allow_html=True)

                st.write("**<mark>Environmental factors</mark>**: Studies are currently underway to explore whether certain exposure to toxins during pregnancy or after birth can increase the risk for developing ASD.", unsafe_allow_html=True)

                st.write("**<mark>Brain differences</mark>**: Differences in certain areas of the brain have been observed in people with ASD, compared to those without ASD. It is not yet known what causes these differences." ,unsafe_allow_html=True)

                st.title("Symptoms of ASD:")
                st.write("1.Avoids or does not keep eye contact")
                st.write("2.Does not respond to name by 9 months of age")
                st.write("3.Does not show facial expressions like happy, sad, angry, and surprised by 9 months of age")
                st.write("4.Lines up toys or other objects and gets upset when order is changed")
                st.write("5.Repeats words or phrases over and over (called echolalia)")
                st.write("6.Plays with toys the same way every time")
                st.write("7.Delayed language skills")
                st.write("8.Delayed movement skills")
                st.write("9.Delayed cognitive or learning skill, etc.")

                st.title("Prevalence Autism in Malaysia")

                st.write("The exact prevalence of Autism Spectrum Disorder (ASD) in Malaysia is not well-established due to a lack of nationwide studies and consistent diagnostic criteria. However, some studies have estimated that the prevalence of ASD in Malaysia is between 1 and 2 per 1000 children. According to to an Ministry of Health (MOH) study in 2005, which use modified checklist for Autism in Toddlers (M-CHAT) screener for ASD, the prevelance in Malaysia is between one and two per 1000 children aged 18 months to three years. The study also found that male children are four times more likely to get ASD than female children.")
                st.markdown(
    "The number of children with <b style='font-size: 20px;'>autism</b> registered with the Department of Sosial Welfare (JKM) has been steadily rising, from <b style='font-size: 20px;'>6991 children in 2013</b> to <b style='font-size: 20px;'>53,323 in 2023</b>. The figures for each year were provided by <b style='font-size: 20px;'>Minister of Women, Family and Community Development, Nancy Shukri</b> in her written reply to parliament last <b style='font-size: 20px;'>July 3, 2024</b>.",
    unsafe_allow_html=True
)



                st.title("World Autism Awareness Day")
                st.write("World Autism Awareness Day is observed on April 2nd each year. Established by the United Nations in 2007, this day aims to raise awareness about autism spectrum disorder (ASD) and promote acceptance and inclusion of individuals with autism worldwide. The day encourages governments, organizations, and communities to take action to improve the lives of people with autism and their families.")
                
            with col2:
                img1 = Image.open("asd_child.jpg")
                st.image(img1, width=300)
                
                img2 = Image.open("causes-of-autism.png")
                st.image(img2, width=400)

                st.write("")
                st.write("")
                st.write("")
            
                img3 = Image.open("autism.png")
                st.image(img3, width=500)

                img4 = Image.open("childrenautism2023.png")
                st.image(img4, width=500)

                st.write("")
                st.write("")
                st.write("")
                         
                img5 = Image.open("licensed-image.jpg")
                st.image(img5, width=400)
   
   
                # Signup Section
    elif selected == "Signup":
        st.title(":iphone: Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Signup"):
        a    dd_userdata(conn, new_user, make_hashes(new_password))



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
        speech_delay = st.selectbox("Speech Delay", options=["Yes", "No"])
        learning_disorder = st.selectbox("Learning Disorder", options=["Yes", "No"])
        genetic_disorders = st.selectbox("Genetic Disorders", options=["Yes", "No"])
        depression = st.selectbox("Depression", options=["Yes", "No"])
        intellectual_disability = st.selectbox("Intellectual Disability", options=["Yes", "No"])
        social_behavioral_issues = st.selectbox("Social/Behavioral Issues", options=["Yes", "No"])
        anxiety_disorder = st.selectbox("Anxiety Disorder", options=["Yes", "No"])
        gender = st.selectbox("Gender (Male=1/Female=0)", options=["Male", "Female"])
        jaundice = st.selectbox("Suffers from Jaundice", options=["Yes", "No"])
        family_history_asd = st.selectbox("Family History with ASD", options=["Yes", "No"])

        if st.button("Diagnose"):
            # Prepare input data for prediction
            input_data = [[
                social_responsiveness,
                age,
                1 if speech_delay == "Yes" else 0,
                1 if learning_disorder == "Yes" else 0,
                1 if genetic_disorders == "Yes" else 0,
                1 if depression == "Yes" else 0,
                1 if intellectual_disability == "Yes" else 0,
                1 if social_behavioral_issues == "Yes" else 0,
                1 if anxiety_disorder == "Yes" else 0,
                1 if gender == "Male" else 0,
                1 if jaundice == "Yes" else 0,
                1 if family_history_asd == "Yes" else 0
            ]]

            # Scale input data
            input_data_scaled = scaler.transform(input_data)

            # Make prediction
            diagnosis = classifier.predict(input_data_scaled)

            # Display result
            result = "Positive" if diagnosis[0] == 1 else "Negative"
            st.success(f"Diagnosis Result: {result}")

            # Generate PDF report
            pdf_path = generate_pdf_result(st.session_state['username'], result, input_data)

            # Provide link to download the PDF
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
        st.session_state['go_to_diagnosis'] = False
        st.success("Logged out successfully.")

    conn.close()  # Close database connection at the end

if __name__ == "__main__":
    main()
