from __future__ import annotations
import streamlit as st
from ui_sidebar import render_sidebar
from pages.round_definitions import show_round_definitions
from pages.score_entry import show_score_entry
from pages.score_history import show_score_history
from pages.pbs_records import show_pbs_records
from pages.competition_results import show_competition_results
from pages.championship_ladder import show_championship_ladder
from pages.recorder_approval import show_recorder_approval
from pages.recorder_management import show_recorder_management
from data_rounds import list_rounds, list_ranges 

st.set_page_config(
    page_title="Archery Score Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# Hide Streamlit's default navigation
st.markdown("""
<style>
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Initialize current page if not set
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Render the sidebar with navigation
render_sidebar()

# Render the selected page
if st.session_state.current_page == "home":
    show_round_definitions()
elif st.session_state.current_page == "score_entry":
    show_score_entry()
elif st.session_state.current_page == "score_history":
    show_score_history()
elif st.session_state.current_page == "pbs_records":
    show_pbs_records()
elif st.session_state.current_page == "competition_results":
    show_competition_results()
elif st.session_state.current_page == "championship_ladder":
    show_championship_ladder()
elif st.session_state.current_page == "recorder_approval":
    show_recorder_approval()
elif st.session_state.current_page == "recorder_management":
    show_recorder_management()
else:
    show_round_definitions()  # Default to home page

# Session state for selection is page-local; simple key is fine
if "ui.selected_round_id" not in st.session_state:
    st.session_state["ui.selected_round_id"] = None

selected_id = st.session_state["ui.selected_round_id"]

try:
    if selected_id is None:
        rounds = list_rounds()
        if not rounds:
            st.info("No rounds defined yet. Contact the recorder to add rounds.")
        else:
            cols = st.columns(3)
            for idx, r in enumerate(rounds):
                with cols[idx % 3]:
                    st.container(border=True)
                    st.subheader(f"🎯 {r['round_name']}")
                    count = r["range_count"]
                    st.caption(f"{count} {'range' if count == 1 else 'ranges'}")
                    if st.button("View Details", key=f"view_round_{r['id']}", use_container_width=True):
                        st.session_state["ui.selected_round_id"] = r["id"]
                        st.rerun()
    else:
        # Selected round details
        ranges = list_ranges(selected_id)
        if not ranges:
            st.error("Round not found or has no ranges.")
            st.session_state["ui.selected_round_id"] = None
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                name = next((r["round_name"] for r in list_rounds() if r["id"] == selected_id), "Selected Round")
                st.subheader(name)
            with col2:
                if st.button("← Back to List", use_container_width=True):
                    st.session_state["ui.selected_round_id"] = None
                    st.rerun()

            total_ends = sum(r["ends_per_range"] for r in ranges)
            total_arrows = total_ends * 6
            st.info(f"📊 Total of {total_ends} ends ({total_arrows} arrows)")
            st.markdown("---")

            for idx, row in enumerate(ranges, 1):
                st.container(border=True)
                st.markdown(f"#### 📍 Range {idx}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Distance", f"{row['distance_m']} m")
                c2.metric("Face Size", f"{row['face_size']} cm")
                arrows = row["ends_per_range"] * 6
                c3.metric("Arrows", f"{arrows} ({row['ends_per_range']} ends)")

            st.markdown("---")
            st.success(f"📖 **Total:** {total_arrows} arrows across {len(ranges)} {'range' if len(ranges) == 1 else 'ranges'}")

except Exception:
    st.error("Something went wrong while loading round definitions.")
