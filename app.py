# streamlit_app.py
import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="Archery Club (st.connection)",
    page_icon="🏹",
    layout="wide"
)

st.title("🏹 Archery Club Score System (st.connection Demo)")
st.write("This app connects to MySQL using the built-in `st.connection`.")

# --- Database Connection ---
try:
    # 1. Initialize the connection.
    # This single line replaces all of db_config.py
    # It automatically reads secrets from [connections.mysql]
    # and handles engine creation and caching.
    conn = st.connection("mysql", type="sql")
    
    st.success("✅ Database connection successful!")

    # --- Fetch Archers ---
    st.header("Club Archers")
    st.write("Displaying archers with their gender and default division.")

    # 2. Define the query
    archer_query = """
        SELECT 
            a.id AS archer_id, 
            a.birth_year, 
            g.gender_code, 
            d.bow_type_code 
        FROM archer a
        JOIN gender g ON a.gender_id = g.id
        JOIN division d ON a.division_id = d.id;
    """
    
    # 3. Run the query.
    # The .query() method handles:
    # - Opening a connection
    # - Running the SQL
    # - Returning a DataFrame
    # - Caching the result (for 10 minutes, set by ttl=600)
    # - Closing the connection
    archers_df = conn.query(archer_query, ttl=600)
    st.dataframe(archers_df)
    
    # --- Fetch Rounds (in a checkbox) ---
    if st.checkbox("Show Available Rounds"):
        st.header("Official Rounds")
        st.write("This query is also cached for 10 minutes.")
        
        rounds_df = conn.query('SELECT * FROM round;', ttl=600)
        st.dataframe(rounds_df)

except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.info("""
        **Please check:**
        1.  Is your MySQL server running in the Codespace (`sudo service mysql start`)?
        2.  Does your `.streamlit/secrets.toml` file exist?
        3.  Does it have the correct `[connections.mysql]` header?
    """)