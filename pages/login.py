import streamlit as st
import mysql.connector
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from utils import get_db_connection  # Assuming this function is in a separate utils.py file

# Function to generate a random reset code
def generate_reset_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Function to send email with the reset code
def send_reset_email(user_email, reset_code):
    try:
        sender_email = "shedrackwambua40@gmail.com"  # Your email
        receiver_email = user_email
        password = "dgin zpom mcro yije"  # Your email password or app password
        
        # Create the email content
        subject = "Password Reset Code"
        body = f"Your password reset code is: {reset_code}. It is valid for 5 minutes."
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Sending the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        st.success("Reset code sent to your email.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to save new password in the database
def update_password(user_email, new_password):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, user_email))
            conn.commit()
            conn.close()
            st.success("Password updated successfully.")
        else:
            st.error("Failed to connect to the database.")
    except mysql.connector.Error as err:
        st.error(f"Error updating password: {err}")

# Function to display the login/signup/forgot password page
def show_login_signup():
    # Initialize session state for user ID if not already set
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    # User Authentication or Sign-up or Forgot Password
    option = st.selectbox("Select an option", ["Login", "Sign Up", "Forgot Password"], key="login_signup_option")

    if option == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = %s AND password = %s ", 
                           (username, password, ))
            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state.user_id = user[0]  # Set user session
                st.session_state.page = "View Past Predictions 📊"  # Automatically set page to "View Past Predictions"
                st.success("Login successful. ")
            else:
                st.error("Invalid credentials or email.")

    elif option == "Sign Up":
        st.subheader("Sign Up")
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        new_email = st.text_input("Enter your email")

        if st.button("Sign Up"):
            # Check if username or email already exists
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = %s OR email = %s", 
                           (new_username, new_email))
            existing_user = cursor.fetchone()

            if existing_user:
                st.error("Username or email already taken")
            else:
                # Insert the new user into the database
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                               (new_username, new_password, new_email))
                conn.commit()
                conn.close()
                st.success("Sign-up successful. You can now log in.")
                st.session_state.user_id = new_username  # Automatically log the user in

    elif option == "Forgot Password":
        st.subheader("Forgot Password")
        email_for_reset = st.text_input("Enter your email to reset password")

        if 'reset_code' not in st.session_state:
            if st.button("Send Reset Code"):
                # Check if email exists in the database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE email = %s", (email_for_reset,))
                user = cursor.fetchone()
                conn.close()

                if user:
                    # Generate a reset code and send it via email
                    reset_code = generate_reset_code()
                    send_reset_email(email_for_reset, reset_code)

                    # Save reset code in session state to validate later
                    st.session_state.reset_code = reset_code
                    st.session_state.reset_code_timestamp = pd.Timestamp.now()

                    # Ask the user to enter the reset code
                    st.session_state.email_for_reset = email_for_reset  # Save email for next step
                    st.text_input("Enter the reset code you received")  # For user to enter the reset code

                else:
                    st.error("Email not found. Please check and try again.")

        if 'reset_code' in st.session_state:
            reset_code_input = st.text_input("Enter the reset code you received")
            new_password = st.text_input("Enter your new password", type="password")

            if st.button("Reset Password"):
                # Validate the reset code and its expiration
                elapsed_time = pd.Timestamp.now() - st.session_state.reset_code_timestamp
                if elapsed_time > pd.Timedelta(minutes=5):
                    st.error("The reset code has expired. Please request a new one.")
                elif reset_code_input == st.session_state.reset_code:
                    update_password(st.session_state.email_for_reset, new_password)
                    st.session_state.reset_code = None  # Clear the reset code after use
                else:
                    st.error("Invalid reset code.")

# Run the function to display the login/signup/forgot password page
show_login_signup()
