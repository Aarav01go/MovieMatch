import streamlit as st
from streamlit_option_menu import option_menu
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="MovieMatch", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1a24 0%, #09090b 100%) !important;
        color: #f4f4f5 !important;
    }
    
    .movie-poster {
        width: 100%;
        aspect-ratio: 2/3;
        object-fit: cover;
        border-radius: 8px;
        border-bottom: 3px solid #e50914;
        margin-bottom: 10px;
    }
    
    header { visibility: hidden; }
    
    div.stButton > button {
        background: #e50914 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
    }
    div.stButton > button:hover {
        background: #f6121d !important;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

selected = option_menu(
    menu_title=None, 
    options=["Home", "Discover", "My List", "Top Picks"], 
    icons=["house", "search", "star", "film"], 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"background-color": "rgba(9, 9, 11, 0.75)", "border-radius": "10px"},
        "nav-link": {"font-weight": "bold"},
        "nav-link-selected": {"background-color": "#e50914"},
    }
)

if 'username' not in st.session_state:
    st.session_state.username = None

col1, col2 = st.columns([1, 4])
with col1:
    if not st.session_state.username:
        with st.form("login_form"):
            user_input = st.text_input("Enter Username")
            if st.form_submit_button("Login"):
                res = requests.post(f"{API_URL}/users", json={"username": user_input})
                if res.status_code == 200:
                    st.session_state.user_id = res.json()["user_id"]
                    st.session_state.username = user_input
                    st.rerun()
    else:
        st.success(f"User: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()

st.write("---")

def get_poster(title):
    colors = ["18181b", "27272a", "09090b"]
    bg = colors[len(title) % len(colors)]
    letter = urllib.parse.quote(title[0].upper()) if title else "M"
    return f"https://placehold.co/400x600/{bg}/e50914?text={letter}&font=montserrat"

if selected == "Home":
    st.markdown("<h1 style='text-align: center; font-weight: 900; font-size: 4rem;'>MovieMatch</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa;'>Unlimited movies, tailored for you.</p>", unsafe_allow_html=True)
    
    st.subheader("Trending Now")
    try:
        trending = requests.get(f"{API_URL}/movies/trending").json()
        cols = st.columns(6)
        for i, movie in enumerate(trending):
            with cols[i]:
                st.markdown(f"<img src='{get_poster(movie['title'])}' class='movie-poster'>", unsafe_allow_html=True)
                st.write(f"**{movie['title']}**")
    except:
        st.error("Backend offline. Start FastAPI server.")

elif selected == "Discover":
    if not st.session_state.username: st.warning("Login first.")
    else:
        q = st.text_input("Search titles...")
        if q:
            results = requests.get(f"{API_URL}/movies/search?q={q}").json()
            cols = st.columns(4)
            for idx, movie in enumerate(results):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.markdown(f"<img src='{get_poster(movie['title'])}' class='movie-poster'>", unsafe_allow_html=True)
                        st.write(f"**{movie['title']}**")
                        st.caption(movie['genres'])
                        
                        with st.expander("AI SYNOPSIS & RATE"):
                            syn_key = f"syn_{movie['movieId']}"
                            if syn_key not in st.session_state:
                                res = requests.get(f"{API_URL}/ai/synopsis?title={urllib.parse.quote(movie['title'])}").json()
                                st.session_state[syn_key] = res.get("synopsis", "")
                            st.caption(st.session_state[syn_key])
                            
                            rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.5, key=f"r_{movie['movieId']}")
                            if st.button("Save", key=f"b_{movie['movieId']}"):
                                requests.post(f"{API_URL}/ratings", json={"user_id": st.session_state.user_id, "movie_id": movie['movieId'], "rating": rating})
                                st.success("Saved!")

elif selected == "My List":
    if not st.session_state.username: st.warning("Login first.")
    else:
        ratings = requests.get(f"{API_URL}/ratings/{st.session_state.user_id}").json()
        if ratings:
            st.dataframe(pd.DataFrame(ratings)[['title', 'rating', 'timestamp']])
        else:
            st.info("No ratings yet.")

elif selected == "Top Picks":
    if not st.session_state.username: st.warning("Login first.")
    else:
        algo = st.selectbox("Engine", ["svd", "knn", "baseline"])
        try:
            recs = requests.get(f"{API_URL}/recommendations/{st.session_state.user_id}?algo={algo}").json()
            cols = st.columns(4)
            for idx, movie in enumerate(recs):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.markdown(f"<img src='{get_poster(movie['title'])}' class='movie-poster'>", unsafe_allow_html=True)
                        st.write(f"**{movie['title']}**")
                        st.caption(f"⭐ {movie['rating']:.1f} Match")
            
            st.write("---")
            mood = st.text_input("What are you in the mood for?")
            if st.button("Re-rank by Mood") and mood:
                res = requests.post(f"{API_URL}/ai/rerank", json={"movies": [m['title'] for m in recs], "mood": mood}).json()
                st.success(res["result"])
        except:
            st.error("Failed to load recommendations.")
