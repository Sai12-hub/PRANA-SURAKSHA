import streamlit as st
import sqlite3
import random
import time
import re
from streamlit_folium import st_folium
import folium

# ---------- Styling ----------
def add_custom_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1605902711622-cfb43c44367e");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .block-container {
            background-color: rgba(71, 167, 98, 0.65);
            padding: 2rem 2rem;
            border-radius: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def add_logo():
    try:
        st.image("./PRANA_SURAKSHA.png", width=80)
    except:
        st.warning("Logo image not found.")

# ---------- Validation ----------
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_mobile(mobile):
    pattern = r'^\d{10}$'
    return re.match(pattern, mobile) is not None

# ---------- Database ----------
def create_user_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT,
            username TEXT,
            mobile TEXT,
            identity TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def reset_user_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("""
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            email TEXT,
            username TEXT,
            mobile TEXT,
            identity TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_user(user_id, email, username, mobile, identity, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, email, username, mobile, identity, password))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("users.db")  # ✅ Fixed typo here
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))  # ✅ Correct column
    user = c.fetchone()
    conn.close()
    return user

# ---------- Ensure table exists ----------
create_user_table()

# ---------- Session State ----------
if 'authenticated_user' not in st.session_state:
    st.session_state['authenticated_user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# ---------- OTP Generator ----------
def send_otp():
    return str(random.randint(100000, 999999))

# ---------- Pages ----------
def login_page():
    add_logo()
    st.title("🔐 Login")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(user_id)
        if user and user[5] == password:
            st.success("Login successful")
            st.session_state['authenticated_user'] = user_id
            st.session_state['page'] = 'home'
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.write("---")
    if st.button("New user? Register here"):
        st.session_state['page'] = 'register'
        st.rerun()

    # 🔧 Developer Tools
    with st.expander("🛠 Developer Tools (Danger Zone)"):
        if st.button("⚠️ Reset User Table (Drop and Recreate)"):
            reset_user_table()
            st.success("✅ User table reset successfully. You can now register fresh users.")

def register_page():
    add_logo()
    st.title("📝 Register")

    user_id = st.text_input("Create User ID")
    email = st.text_input("Email")
    username = st.text_input("Username")
    mobile = st.text_input("Mobile Number")
    identity = st.text_input("Aadhar/PAN/Voter ID")
    password = st.text_input("Password", type="password")

    if 'otp_sent' not in st.session_state:
        st.session_state['otp_sent'] = False

    if st.button("Send OTP"):
        if not is_valid_email(email):
            st.error("❌ Invalid Email")
        elif not is_valid_mobile(mobile):
            st.error("❌ Invalid Mobile Number (must be 10 digits)")
        elif get_user(user_id):
            st.error("❌ User ID already exists.")
        else:
            st.session_state.generated_otp = send_otp()
            st.session_state.otp_sent = True
            st.success(f"✅ OTP sent (simulated): {st.session_state.generated_otp}")

    if st.session_state.otp_sent:
        entered_otp = st.text_input("Enter OTP")
        if st.button("Submit"):
            if entered_otp == st.session_state.get("generated_otp"):
                insert_user(user_id, email, username, mobile, identity, password)
                st.success("Registration successful. Please login.")
                st.session_state['otp_sent'] = False
                st.session_state['page'] = 'login'
                st.rerun()
            else:
                st.error("Invalid OTP")

    st.write("---")
    if st.button("Back to Login"):
        st.session_state['page'] = 'login'
        st.rerun()

def home_page():
    add_logo()
    st.markdown("<h2 style='text-align:center;'>WELCOME TO PRANA SURAKSHA</h2>", unsafe_allow_html=True)
    st.title(f"🏠 Welcome, {st.session_state['authenticated_user']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚨 Emergency"):
            st.session_state['page'] = 'emergency'
            st.rerun()
    with col2:
        if st.button("🚦 Signal Control"):
            st.session_state['page'] = 'signal'
            st.rerun()

    if st.button("👤 View Profile"):
        st.session_state['page'] = 'profile'
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state['authenticated_user'] = None
        st.session_state['page'] = 'login'
        st.rerun()

def profile_page():
    add_logo()
    st.title("👤 Profile")

    user_id = st.session_state['authenticated_user']
    user = get_user(user_id)

    st.write(f"**User ID:** {user_id}")
    st.write(f"**Username:** {user[2]}")
    st.write(f"**Email:** {user[1]}")
    st.write(f"**Mobile:** {user[3]}")
    st.write(f"**ID Proof:** {user[4]}")

    if st.button("🔙 Back"):
        st.session_state['page'] = 'home'
        st.rerun()

def emergency_page():
    add_logo()
    st.title("🚑 Emergency Connect")

    hospitals = {
        "Apollo Hospital": {"location": (17.4291, 78.4080), "contact": "040-23607777"},
        "KIMS Hospital": {"location": (17.4375, 78.4483), "contact": "040-44885000"},
        "Yashoda Hospital": {"location": (17.4300, 78.3926), "contact": "040-45674567"},
        "Rainbow Hospital": {"location": (17.4422, 78.4786), "contact": "040-22334455"},
        "Fortis Healthcare": {"location": (17.4350, 78.3942), "contact": "040-33446677"}
    }

    if 'emergency_code' not in st.session_state or st.session_state.get('last_page') != 'emergency':
        st.session_state['emergency_code'] = str(random.randint(100000, 999999))
        st.session_state['last_page'] = 'emergency'
        st.session_state['assigned_hospital'] = random.choice(list(hospitals.keys()))

    assigned = st.session_state['assigned_hospital']
    hospital_lat, hospital_lon = hospitals[assigned]['location']
    user_lat, user_lon = 17.4325, 78.4456

    st.success(f"Connected to: **{assigned}**")
    st.success(f"Emergency Code: `{st.session_state['emergency_code']}`")

    st.markdown("### 🏥 Nearby Hospitals:")
    for name, data in hospitals.items():
        st.markdown(f"- **{name}** | 📞 {data['contact']}")

    url = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{hospital_lat},{hospital_lon}"
    st.markdown(f"[🧭 Directions to {assigned} →](%s)" % url)

    m = folium.Map(location=[user_lat, user_lon], zoom_start=13)
    folium.Marker([user_lat, user_lon], popup="You", icon=folium.Icon(color="green")).add_to(m)
    for name, data in hospitals.items():
        lat, lon = data['location']
        folium.Marker([lat, lon], tooltip=name, popup=data['contact'],
                      icon=folium.Icon(color="red" if name == assigned else "blue")).add_to(m)

    st_folium(m, width=700, height=500)

    if st.button("🔙 Back"):
        st.session_state['page'] = 'home'
        st.rerun()

def signal_control_page():
    add_logo()
    st.title("🚦 Signal Control")

    code = st.text_input("Enter Emergency Code")

    if st.button("Activate Signal"):
        if code == st.session_state.get('emergency_code'):
            st.success("Signal turned GREEN. Please cross.")
            time.sleep(3)
            st.info("Signal reset to normal.")
            st.session_state['emergency_code'] = None
        else:
            st.error("Invalid Code")

    if st.button("🔙 Back"):
        st.session_state['page'] = 'home'
        st.rerun()

# ---------- Main ----------
def main():
    add_custom_background()

    if st.session_state['authenticated_user'] is None:
        if st.session_state['page'] == 'login':
            login_page()
        elif st.session_state['page'] == 'register':
            register_page()
    else:
        if st.session_state['page'] == 'home':
            home_page()
        elif st.session_state['page'] == 'profile':
            profile_page()
        elif st.session_state['page'] == 'emergency':
            emergency_page()
        elif st.session_state['page'] == 'signal':
            signal_control_page()

# ---------- Run App ----------
if __name__ == "__main__":
    main()
