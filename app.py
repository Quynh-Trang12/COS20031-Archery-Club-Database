import streamlit as st
import pandas as pd

# --- Page Configuration ---
# Set the title, icon, and layout for your app
st.set_page_config(
    page_title="Archery Score Hub",
    page_icon="🎯",
    layout="wide"
)

# --- Database Connection ---
# Uses Streamlit's built-in connection management.
# .streamlit/secrets.toml file in your app's root
# directory with your MySQL credentials.
@st.cache_resource
def get_db_connection():
    """Establishes a cached connection to the MySQL database."""
    try:
        conn = st.connection("mysql", type="sql")
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# --- Session State Initialization ---
# This dictionary will hold our mock archer data for the simulation.
# In a real app, you'd query this from the `archer` table.
# NOTE: The `archer` table in your SQL file needs a `name` column to match
# [cite_start]your Figma design and project requirements[cite: 655].
MOCK_ARCHERS = {
    1: "Hoang Dung Nguyen",
    2: "Ngoc Quynh Trang Le",
    3: "Truong Que An Pham"
}

# Initialize session state variables if they don't exist
if 'archer_id' not in st.session_state:
    st.session_state.archer_id = 1 # Default to first archer
if 'archer_name' not in st.session_state:
    st.session_state.archer_name = MOCK_ARCHERS[1]
if 'is_recorder' not in st.session_state:
    st.session_state.is_recorder = False

# --- Sidebar Login Simulation ---
# This section simulates the login and role-switching from your Figma design.
st.sidebar.header("User Simulation")
selected_archer_id = st.sidebar.selectbox(
    "Log in as:",
    options=MOCK_ARCHERS.keys(),
    format_func=lambda id: MOCK_ARCHERS[id],
    key='login_select'
)

# Update session state when the user changes
st.session_state.archer_id = selected_archer_id
st.session_state.archer_name = MOCK_ARCHERS[selected_archer_id]

# The "Switch to Recorder" toggle
st.session_state.is_recorder = st.sidebar.toggle(
    "Act as Recorder",
    value=st.session_state.is_recorder,
    key='recorder_toggle'
)
st.sidebar.divider()

# --- Navigation Definition ---
# We will import and add our page modules here one by one.
# For now, create empty lists.

# 1. Import view modules (we will uncomment these as we go)
# from views import (
#     score_entry, 
#     score_history, 
#     pbs_records, 
#     competition_results, 
#     championship_ladder, 
#     round_definitions, 
#     admin_approval, 
#     admin_management
# )

# 2. Define the pages
archer_pages = [
    # Page(score_entry.show, title="Score Entry", icon="🎯"),
    # Page(score_history.show, title="My Score History", icon="📊"),
    # Page(pbs_records.show, title="PBs & Records", icon="🏆"),
    # Page(competition_results.show, title="Competition Results", icon="🏁"),
    # Page(championship_ladder.show, title="Championship Ladder", icon="🥇"),
    # Page(round_definitions.show, title="Round Definitions", icon="📖"),
]

admin_pages = [
    # Page(admin_approval.show, title="Score Approval", icon="🔒"),
    # Page(admin_management.show, title="Admin Management", icon="⚙️"),
]

# 3. Build the final navigation list
nav_pages = archer_pages[:]  # Start with a copy of archer pages

if st.session_state.is_recorder:
    nav_pages.extend(admin_pages)  # Add admin pages if user is recorder

# 4. Run the navigation or show the welcome page
if nav_pages:
    # If we have pages, run the navigation
    pg = st.navigation(nav_pages)
    
    # --- Shared Header ---
    st.header(f"Welcome, {st.session_state.archer_name}!")
    
    # Show role-specific info
    is_admin_page = pg.title in ["Score Approval", "Admin Management"]
    if st.session_state.is_recorder and is_admin_page:
        st.info("You are in **Recorder Mode**.", icon="🔒")
    else:
        st.info("You are in **Archer Mode**.", icon="🏹")
    
    # --- Run the selected page's content ---
    pg.run()
    
else:
    # --- Default Welcome Page (if no views are loaded) ---
    st.header(f"Welcome, {st.session_state.archer_name}!")
    if st.session_state.is_recorder:
        st.info("You are currently in **Recorder Mode**.", icon="🔒")
    else:
        st.info("You are in **Archer Mode**.", icon="🏹")

    st.subheader("Welcome to the Archery Score Hub")
    st.markdown("We are building the app. The pages will appear in the sidebar as we create them.")
    st.image("https://i.imgur.com/gY974rU.png", caption="Figma Design Preview", width=600)