import streamlit as st
import sqlite3
import hashlib
import time

# Set page layout
st.set_page_config(layout="wide")

# Define the new database name
DATABASE_NAME = 'naz.db'

# Function to hash passwords
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Initialize database connection
def init_db_connection():
    """Initialize and return a new SQLite database connection."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Removed info notification
        return conn
    except sqlite3.DatabaseError as e:
        st.error(f"Database connection failed: {e}")
        return None

# Create a new table if it doesn't exist
def create_usertable(conn):
    """Create a new table for user data if it doesn't exist."""
    try:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
        conn.commit()
        # Removed info notification
    except sqlite3.DatabaseError as e:
        st.error(f"Error creating table: {e}")

# Add new user data
def add_userdata(conn, username, password):
    """Insert a new user into the userstable."""
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
    """Check if the user exists and the password is correct."""
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
        return c.fetchall()
    except sqlite3.DatabaseError as e:
        st.error(f"Login error: {e}")
        return []

# Main application function
def main():
    conn = init_db_connection()
    if conn is None:
        st.stop()  # Stop execution if database connection failed

    create_usertable(conn)  # Ensure the table is created at the start

    # Sidebar menu for navigation using radio buttons
    menu = ["Signup", "Login"]
    selected = st.sidebar.radio("Start Here!", menu)

    # Signup Section
    if selected == "Signup":
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
            prog = st.progress(0)
            for per_comp in range(100):
                time.sleep(0.05)
                prog.progress(per_comp + 1)
            if result:
                st.success("Logged In as {}".format(username))
                st.warning("Go to Home Menu!")
            else:
                st.warning("Incorrect Username/Password")

# Run the main function
if __name__ == '__main__':
    main()
