import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load the dataset
file_path = "asd_data_csv.csv"
asd_data_csv = pd.read_csv(file_path)

# Separate input features (X) and output label (Y)
X = asd_data_csv.drop(columns='Outcome')  # X contains input features
Y = asd_data_csv['Outcome']               # Y contains output label

# Create a new StandardScaler object
scaler = StandardScaler()

# Fit the scaler with the input features
X_standardized = scaler.fit_transform(X)

# Train Test Split
X_train, X_test, Y_train, Y_test = train_test_split(X_standardized, Y, test_size=0.2, stratify=Y, random_state=42)

# Initialize the Random Forest classifier
classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the classifier on the training data
classifier.fit(X_train, Y_train)

# Make predictions on the test data
test_predictions = classifier.predict(X_test)
test_accuracy = accuracy_score(test_predictions, Y_test)

# Save the trained classifier to a file
with open("autism_random_forest.pkl", "wb") as file:
    pickle.dump(classifier, file)

# Save the fitted scaler to a file
with open('scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

# Streamlit web app
st.title('Autism Diagnosis')

# Custom CSS to set background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;   
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("""
## Enter the values for the input features to predict whether a person has Autism Spectrum Disorder (ASD) or not.
""")

# Sidebar with information about autism
st.sidebar.title('About Autism')
st.sidebar.write("""
Autism, or autism spectrum disorder (ASD), is a neurodevelopmental condition that manifests in early childhood and affects an individual's social interactions, communication abilities, and behavior. It is characterized by a wide spectrum of symptoms, which can range from mild to severe. Common features include difficulties in understanding and responding to social cues, repetitive behaviors or interests, and challenges in verbal and nonverbal communication. Each person with autism experiences a unique combination of symptoms, leading to a diverse range of abilities and challenges..
""")

st.sidebar.write("""
In Malaysia, as in many countries worldwide, the prevalence of autism has been a topic of increasing awareness and research. While specific prevalence rates can vary based on different studies and methodologies, estimates suggest that autism affects a significant number of individuals across the country. Access to accurate data on autism prevalence is crucial for informing healthcare policies, educational strategies, and support services for individuals and families affected by ASD. Efforts to enhance awareness, early detection, and intervention are ongoing to improve outcomes and quality of life for those living with autism in Malaysia.
""")

st.sidebar.write("""
Government agencies, non-governmental organizations, and research institutions in Malaysia play pivotal roles in studying and addressing autism spectrum disorder. They work collaboratively to promote understanding, support families, and advocate for inclusive practices in education and society. By fostering a better understanding of autism and providing comprehensive support systems, Malaysia aims to empower individuals with ASD to thrive and contribute meaningfully to their communities.
""")

# Button in the sidebar
if st.sidebar.button('Learn More'):
    st.sidebar.write("""
    Visit the [NASOM(The National Autism Society Of Malaysia)](https://www.nasom.org.my/) to learn more about autism.
    """)


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
