import streamlit as st
import random
import time
from streamlit_folium import st_folium
import folium

# ---------- Styling: Background and Branding ----------
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
    st.image("C:/Users/gunis/OneDrive/Desktop/streamlit_run/PRANA_SURAKSHA.png", width=80)

# ---------- Session State Initialization ----------
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {}
if 'authenticated_user' not in st.session_state:
    st.session_state['authenticated_user'] = None

# ---------- Utility ----------
def send_otp():
    return str(random.randint(100000, 999999))

# ---------- Login ----------
def login_page():
    add_logo()
    st.title("🔐 Login")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_db = st.session_state['user_db']
        if user_id in user_db and user_db[user_id]['password'] == password:
            st.success("Login successful")
            st.session_state['authenticated_user'] = user_id
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------- Register ----------
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
        st.session_state.generated_otp = send_otp()
        st.session_state.otp_sent = True
        st.success(f"OTP sent to your number (simulated): {st.session_state.generated_otp}")

    if st.session_state.otp_sent:
        entered_otp = st.text_input("Enter OTP")

        if st.button("Submit"):
            if user_id in st.session_state['user_db']:
                st.error("User ID already exists. Please choose another.")
            elif entered_otp == st.session_state.get("generated_otp"):
                st.session_state['user_db'][user_id] = {
                    'email': email,
                    'username': username,
                    'mobile': mobile,
                    'identity': identity,
                    'password': password
                }
                st.success("Registration successful. Please login.")
                st.session_state['otp_sent'] = False
                st.rerun()
            else:
                st.error("Invalid OTP")

# ---------- Home ----------
def home_page():
    add_logo()
    st.markdown("<h2 style='text-align:center; color:#2E8B57;'>WELCOME TO PRANA SURAKSHA</h2>", unsafe_allow_html=True)
    st.title(f"🏠 Welcome, {st.session_state['authenticated_user']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚨 Emergency"):
            st.session_state['page'] = 'emergency'
            st.rerun()
    with col2:
        if st.button("🚦 Signal Control"):
            st.session_state['page'] = 'signal_control'
            st.rerun()

# ---------- Emergency ----------
# ---------- Emergency ----------
from streamlit_folium import st_folium
import folium

# ---------- Emergency ----------
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

    # Assign emergency code and hospital once per new page visit
    if 'emergency_code' not in st.session_state or st.session_state.get('last_page') != 'emergency':
        st.session_state['emergency_code'] = str(random.randint(100000, 999999))
        st.session_state['last_page'] = 'emergency'
        st.session_state['assigned_hospital'] = random.choice(list(hospitals.keys()))

    assigned = st.session_state['assigned_hospital']
    hospital_lat, hospital_lon = hospitals[assigned]['location']

    st.info("Connecting to nearest hospital...")
    time.sleep(1.5)
    st.success(f"Connected to: **{assigned}**")
    st.success(f"Emergency code generated: `{st.session_state['emergency_code']}`")

    # Nearby hospital list
    st.markdown("### 🏥 Nearby Hospitals:")
    for name, data in hospitals.items():
        st.markdown(f"- **{name}** | 📞 {data['contact']}")

    # Optional: Simulated user location (could be dynamic later)
    user_lat, user_lon = 17.4325, 78.4456  # Example: Banjara Hills, Hyderabad

    # Directions button
    google_maps_url = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{hospital_lat},{hospital_lon}"
    st.markdown(f"[🧭 Click here for directions to {assigned} →](%s)" % google_maps_url)

    # Map
    st.markdown("### 🗺️ Map View of Hospitals")
    m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

    # Add user marker
    folium.Marker(
        [user_lat, user_lon],
        popup="Your Location",
        icon=folium.Icon(color="green", icon="user")
    ).add_to(m)

    # Add hospital markers
    for name, data in hospitals.items():
        lat, lon = data['location']
        folium.Marker(
            [lat, lon],
            popup=f"{name}<br>📞 {data['contact']}",
            tooltip=name,
            icon=folium.Icon(color="red" if name == assigned else "blue", icon="plus-sign")
        ).add_to(m)

    st_folium(m, width=700, height=500)



# ---------- Signal Control ----------
def signal_control_page():
    add_logo()
    st.title("🚦 Traffic Signal Control")
    entered_code = st.text_input("Enter Emergency Code")

    if st.button("Activate Signal"):
        if entered_code == st.session_state.get('emergency_code'):
            st.success("Signal turned GREEN. Please cross.")
            time.sleep(3)
            st.info("Vehicle crossed. Signal is back to normal.")
            st.session_state['emergency_code'] = None
        else:
            st.error("Invalid Code")

# ---------- Profile Page ----------
def profile_page():
    add_logo()
    st.title("👤 User Profile")

    user_id = st.session_state['authenticated_user']
    user_data = st.session_state['user_db'].get(user_id, {})

    st.write("### Basic Information")
    st.write(f"**User ID**: {user_id}")
    st.write(f"**Email**: {user_data.get('email')}")
    st.write(f"**Username**: {user_data.get('username')}")
    st.write(f"**Mobile**: {user_data.get('mobile')}")
    st.write(f"**ID Proof**: {user_data.get('identity')}")

# ---------- Main Router ----------
def main():
    add_custom_background()

    if st.session_state['authenticated_user'] is None:
        st.sidebar.markdown("## 🔑 Authentication")
        choice = st.sidebar.radio("Go to", ["Login", "Register"])
        if choice == "Login":
            login_page()
        else:
            register_page()
    else:
        st.sidebar.markdown(f"👤 Logged in as: `{st.session_state['authenticated_user']}`")
        st.sidebar.markdown("## 📋 Menu")
        choice = st.sidebar.radio("Navigate", ["Home", "Profile", "Emergency", "Signal Control", "Logout"])

        if choice == "Home":
            home_page()
        elif choice == "Profile":
            profile_page()
        elif choice == "Emergency":
            emergency_page()
        elif choice == "Signal Control":
            signal_control_page()
        elif choice == "Logout":
            st.session_state['authenticated_user'] = None
            st.experimental_rerun()

# ---------- Run App ----------
if __name__ == "__main__":
    main()
