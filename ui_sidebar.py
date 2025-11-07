# ui_sidebar.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import streamlit as st

from auth import load_member_profile  # dependency injected at module level

# ---------- Paths & constants ----------

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"

HOME_PAGE = "app.py"

# Page identifiers for navigation
PUBLIC_PAGES = [
    ("🏆 Competition Results", "competition_results"),
    ("🥇 Championship Ladder", "championship_ladder"),
]

ARCHER_PAGES = [
    ("🎯 Score Entry", "score_entry"),
    ("📊 My Scores", "score_history"),
    ("🏅 Personal Bests", "pbs_records"),
]

RECORDER_PAGES = [
    ("✅ Approve Scores", "recorder_approval"),
    ("⚙️ Manage Club", "recorder_management"),
]

# ---------- Lightweight auth model ----------

@dataclass
class AuthState:
    logged_in: bool = False
    id: int | None = None
    name: str | None = None
    is_recorder: bool = False
    av: str | None = None

def _get_auth() -> AuthState:
    raw = st.session_state.get("auth")
    if not raw:
        return AuthState()
    return AuthState(
        logged_in=bool(raw.get("logged_in")),
        id=raw.get("id"),
        name=raw.get("name"),
        is_recorder=bool(raw.get("is_recorder")),
        av=raw.get("av"),
    )

def _set_auth(a: AuthState) -> None:
    st.session_state["auth"] = {
        "logged_in": a.logged_in,
        "id": a.id,
        "name": a.name,
        "is_recorder": a.is_recorder,
        "av": a.av,
    }

def _reset_auth() -> None:
    _set_auth(AuthState())

# ---------- File helpers (decoupled from UI) ----------

def _exists(rel_path: str) -> bool:
    # Paths are resolved relative to this file (same dir as app.py)
    return (BASE_DIR / rel_path).exists()

# ---------- Navigation model ----------

def _visible_sections(auth: AuthState) -> dict[str, list[tuple[str, str]]]:
    """
    Build a pure data model of navigation sections -> [(label, page_id), ...]
    """
    sections = {
        "Home": [("🏠 Home", "home")],
        "Public": [],
    }

    # Public pages always visible
    sections["Public"] = PUBLIC_PAGES.copy()

    # Archer (logged-in but not recorder)
    if auth.logged_in and not auth.is_recorder:
        sections["Archer"] = ARCHER_PAGES.copy()

    # Recorder
    if auth.logged_in and auth.is_recorder:
        sections["Recorder"] = RECORDER_PAGES.copy()

    return sections

# ---------- UI panels (small & focused) ----------

def _render_login_panel(auth: AuthState) -> None:
    if auth.logged_in:
        return
    with st.form("login_form", clear_on_submit=False):
        member_id_str = st.text_input("Member ID", placeholder="Enter numeric Member ID")
        submitted = st.form_submit_button("Log in", use_container_width=True)
    if not submitted:
        return

    try:
        member_id = int(member_id_str)
    except ValueError:
        st.error("Please enter a valid numeric Member ID.")
        return

    profile = load_member_profile(member_id)
    if not profile:
        st.error("Member ID not found.")
        return

    _set_auth(AuthState(
        logged_in=True,
        id=profile["id"],
        name=profile["full_name"],
        is_recorder=profile["is_recorder"],
        av=profile["av_number"],
    ))
    st.success("Login successful!")
    st.rerun()

def _render_profile_panel(auth: AuthState) -> None:
    if not auth.logged_in:
        return
    st.success("👤 Logged in")
    st.write(f"**{auth.name}**")
    if auth.av:
        st.caption(f"AV: {auth.av}")
    if st.button("Logout", use_container_width=True):
        _reset_auth()
        st.rerun()

def _render_nav(sections: dict[str, list[tuple[str, str]]]) -> None:
    st.subheader("Navigation")
    
    # Home first
    for label, page_id in sections.get("Home", []):
        if st.button(label, key=f"nav_{page_id}", use_container_width=True,
                    type="primary" if st.session_state.current_page == page_id else "secondary"):
            st.session_state.current_page = page_id
            st.rerun()

    # Remaining sections in order
    ordered = ["Archer", "Public", "Recorder"]
    for sec in ordered:
        links = sections.get(sec)
        if not links:
            continue
        st.markdown(f"**{sec}**")
        for label, page_id in links:
            if st.button(label, key=f"nav_{page_id}", use_container_width=True,
                        type="primary" if st.session_state.current_page == page_id else "secondary"):
                st.session_state.current_page = page_id
                st.rerun()

# ---------- Public API ----------

def render_sidebar() -> None:
    """
    Orchestrates the sidebar: title -> login/profile -> navigation -> footer.
    Minimal branching; rendering is delegated to focused helpers.
    """
    auth = _get_auth()

    with st.sidebar:
        st.title("🏹 Archery Club")
        st.markdown("---")

        # Auth area
        if auth.logged_in:
            _render_profile_panel(auth)
        else:
            _render_login_panel(auth)

        st.markdown("---")

        # Nav (computed as pure data, then rendered)
        sections = _visible_sections(auth)
        _render_nav(sections)

        st.markdown("---")
        st.caption("Archery Club Dashboard v2.0")
