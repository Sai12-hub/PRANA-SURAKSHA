import os
import re
import sqlite3
import smtplib
from uuid import uuid4
from random import randint
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium

# --- Load Gmail credentials from .env ---
load_dotenv()
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

OTP_CACHE = {}

# --- Database Setup ---
def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            address TEXT,
            id_type TEXT,
            id_number TEXT,
            password TEXT,
            photo TEXT,
            verified INTEGER DEFAULT 0,
            token TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(email, name, address, id_type, id_number, password, photo, token):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (email, name, address, id_type, id_number, password, photo, token) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, name, address, id_type, id_number, password, photo, token))
    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_password(email, new_password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
    conn.commit()
    conn.close()

def send_verification_email(to_email, token):
    link = f"http://localhost:8501/?verify_token={token}"
    message = f"""Subject: Verify Your SmarT CrosS Account\n\nClick the link to verify your account:\n{link}"""
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, to_email, message)
        st.success(f"Verification link sent to {to_email}.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def send_otp_email(to_email):
    otp = str(randint(100000, 999999))
    OTP_CACHE[to_email] = otp
    message = f"""Subject: SmarT CrosS OTP Verification\n\nYour OTP code is: {otp}"""
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, to_email, message)
        st.success(f"OTP sent to {to_email}.")
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def show_emergency_map():
    st.subheader("Nearby Hospitals")
    m = folium.Map(location=[17.385044, 78.486671], zoom_start=13)
    hospitals = [
        ("Apollo Hospital", 17.414, 78.448),
        ("Yashoda Hospital", 17.407, 78.481),
        ("CARE Hospital", 17.435, 78.449),
    ]
    for name, lat, lon in hospitals:
        folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=700, height=500)

def main():
    st.set_page_config("SmarT CrosS")
    create_user_table()

    # Handle verification link
    query_params = st.experimental_get_query_params()
    if "verify_token" in query_params:
        token = query_params["verify_token"][0]
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET verified = 1 WHERE token = ?", (token,))
        conn.commit()
        st.success("Your email has been verified successfully!")
        st.stop()

    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'

    if st.session_state['page'] == 'main':
        st.title("Welcome to SmarT CrosS")
        if st.button("Login"):
            st.session_state['page'] = 'login'
        if st.button("Register"):
            st.session_state['page'] = 'register'

    elif st.session_state['page'] == 'register':
        st.title("Register")
        name = st.text_input("Full Name")
        address = st.text_input("Address")
        email = st.text_input("Email")
        id_type = st.selectbox("ID Type", ["Aadhar", "PAN", "Driving License"])
        id_number = st.text_input("ID Number")
        password = st.text_input("Password", type="password")
        photo = st.file_uploader("Upload Profile Photo", type=['jpg', 'png'])

        if st.button("Send Verification Link"):
            if is_valid_email(email):
                token = uuid4().hex
                photo_path = ""
                if photo:
                    os.makedirs("uploads", exist_ok=True)
                    photo_path = f"uploads/{email}.jpg"
                    with open(photo_path, "wb") as f:
                        f.write(photo.read())
                insert_user(email, name, address, id_type, id_number, password, photo_path, token)
                send_verification_email(email, token)
            else:
                st.error("Invalid email.")

        if st.button("Back to Main"):
            st.session_state['page'] = 'main'

    elif st.session_state['page'] == 'login':
        st.title("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = get_user(email)
            if user and user[5] == password:
                if user[7] == 1:
                    st.session_state['user'] = user
                    st.session_state['page'] = 'home'
                else:
                    st.error("Please verify your email before logging in.")
            else:
                st.error("Invalid credentials.")

        if st.button("Forgot Password"):
            user = get_user(email)
            if user:
                send_otp_email(email)
                st.session_state['reset_email'] = email
                st.session_state['page'] = 'reset'
            else:
                st.error("Email not found.")

        if st.button("Back"):
            st.session_state['page'] = 'main'

    elif st.session_state['page'] == 'reset':
        st.title("Reset Password")
        otp = st.text_input("Enter OTP")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Reset Password"):
            email = st.session_state.get('reset_email')
            if OTP_CACHE.get(email) == otp:
                update_password(email, new_pass)
                st.success("Password updated.")
                st.session_state['page'] = 'login'
            else:
                st.error("Invalid OTP.")

    elif st.session_state['page'] == 'home':
        user = st.session_state.get('user')
        st.title(f"Welcome {user[1]}")

        if st.button("Emergency"):
            show_emergency_map()
            st.session_state['emergency_code'] = randint(10000, 99999)

        if 'emergency_code' in st.session_state:
            st.success(f"Generated Emergency Code: {st.session_state['emergency_code']}")

        if st.button("Signal Control"):
            st.info("Signal Control feature coming soon.")

        if st.button("Logout"):
            st.session_state.clear()

if __name__ == '__main__':
    main()
