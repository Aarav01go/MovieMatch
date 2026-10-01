import streamlit as st
from streamlit_option_menu import option_menu
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="MovieMatch", layout="wide")

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
        transition: transform 0.3s;
    }
    
    .movie-poster:hover {
        transform: scale(1.02);
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
    
    .back-btn > button {
        background: #3f3f46 !important;
        width: auto !important;
        padding: 0.5rem 2rem !important;
    }
    .back-btn > button:hover {
        background: #52525b !important;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

if 'username' not in st.session_state:
    st.session_state.username = None
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None

@st.cache_data(ttl=3600)
def get_poster(title):
    try:
        res = requests.get(f"http://www.omdbapi.com/?apikey=thewdb&t={urllib.parse.quote(title)}").json()
        if res.get("Response") == "True" and res.get("Poster") and res.get("Poster") != "N/A":
            return res.get("Poster")
    except:
        pass
    colors = ["18181b", "27272a", "09090b"]
    bg = colors[len(title) % len(colors)]
    letter = urllib.parse.quote(title[0].upper()) if title else "M"
    return f"https://placehold.co/400x600/{bg}/e50914?text={letter}&font=montserrat"

# --- LOGIN SCREEN ---
if not st.session_state.username:
    st.markdown("<h1 style='text-align: center; font-weight: 900; font-size: 5rem; margin-top: 10vh;'>MovieMatch</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa; font-size: 1.5rem;'>Unlimited movies, tailored for you.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        user_input = st.text_input("Username", placeholder="Enter your username to begin...", label_visibility="collapsed")
        if st.button("Enter MovieMatch", use_container_width=True):
            if user_input:
                res = requests.post(f"{API_URL}/users", json={"username": user_input})
                if res.status_code == 200:
                    st.session_state.user_id = res.json()["user_id"]
                    st.session_state.username = user_input
                    st.rerun()
    st.stop()



# --- FULL SCREEN MOVIE DETAILS ---
if st.session_state.selected_movie:
    movie = st.session_state.selected_movie
    
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅ Back to Browse"):
        st.session_state.selected_movie = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        real_poster = get_poster(movie['title'])
        st.markdown(f"<img src='{real_poster}' style='width: 100%; border-radius: 12px; border-bottom: 4px solid #e50914; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<h1 style='font-size: 4rem; margin-bottom: 0; line-height: 1.1;'>{movie['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #a1a1aa; font-size: 1.2rem; margin-top: 0.5rem;'>{movie['genres']}</p>", unsafe_allow_html=True)
        
        syn_key = f"syn_{movie['movieId']}"
        if syn_key not in st.session_state:
            with st.spinner("Generating AI Synopsis..."):
                try:
                    res = requests.get(f"{API_URL}/ai/synopsis?title={urllib.parse.quote(movie['title'])}").json()
                    st.session_state[syn_key] = res.get("synopsis", "")
                except:
                    st.session_state[syn_key] = "Synopsis unavailable."
        
        st.markdown("### 📝 Synopsis")
        st.write(st.session_state[syn_key])
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### ⭐ Rate this Movie")
        rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.5, key=f"r_{movie['movieId']}")
        if st.button("Save Rating", key=f"b_{movie['movieId']}"):
            requests.post(f"{API_URL}/ratings", json={"user_id": st.session_state.user_id, "movie_id": movie['movieId'], "rating": rating})
            st.success("Saved! This movie has been added to your Completed list.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📅 Add to Plan to Watch", key=f"ptw_{movie['movieId']}"):
            requests.post(f"{API_URL}/watchlist", json={"user_id": st.session_state.user_id, "movie_id": movie['movieId']})
            st.success("Added to Plan to Watch!")
            
    st.markdown("<hr style='border-color: #3f3f46; margin: 3rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Recommendations according to this")
    
    @st.cache_data(ttl=60)
    def get_similar_movies(movie_id):
        return requests.get(f"{API_URL}/movies/similar/{movie_id}").json()
    
    try:
        similar = get_similar_movies(movie['movieId'])
        if similar:
            cols = st.columns(6)
            for i, sim_movie in enumerate(similar):
                with cols[i]:
                    st.markdown(f"<img src='{get_poster(sim_movie['title'])}' class='movie-poster'>", unsafe_allow_html=True)
                    st.write(f"**{sim_movie['title']}**")
                    if st.button("Open", key=f"sim_v_{sim_movie['movieId']}_{i}"):
                        st.session_state.selected_movie = sim_movie
                        st.rerun()
        else:
            st.info("No recommendations found.")
    except Exception as e:
        st.error(f"Failed to load recommendations.")
        
    st.stop()

# --- MAIN NAVIGATION ---
col1, col2 = st.columns([8, 2])
with col1:
    selected = option_menu(
        menu_title=None, 
        options=["Home", "Discover", "My List", "Top Picks"], 
        icons=["house", "search", "star", "film"], 
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"background-color": "rgba(9, 9, 11, 0.75)", "border-radius": "10px", "padding": "0", "margin": "0"},
            "nav-link": {"font-weight": "bold", "margin": "0 5px"},
            "nav-link-selected": {"background-color": "#e50914"},
        }
    )
with col2:
    st.markdown(f"<div style='text-align: right; margin-top: 10px; color: #a1a1aa;'>👤 <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.username = None
        st.session_state.user_id = None
        st.rerun()

st.write("---")

def render_movie_card(movie, col_idx):
    st.markdown(f"<img src='{get_poster(movie['title'])}' class='movie-poster'>", unsafe_allow_html=True)
    st.write(f"**{movie['title']}**")
    if 'rating' in movie:
        st.caption(f"⭐ {movie['rating']:.1f} Match")
    else:
        st.caption(movie['genres'])
    if st.button("Open", key=f"open_{movie['movieId']}_{col_idx}"):
        st.session_state.selected_movie = movie
        st.rerun()

@st.cache_data(ttl=60)
def get_trending_movies():
    return requests.get(f"{API_URL}/movies/trending").json()

@st.cache_data(ttl=60)
def get_recommendations_cached(user_id, algo):
    return requests.get(f"{API_URL}/recommendations/{user_id}?algo={algo}").json()

if selected == "Home":
    st.markdown("<h1 style='text-align: center; font-weight: 900; font-size: 3rem;'>Welcome Back</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa; margin-bottom: 3rem;'>Here is what is trending today.</p>", unsafe_allow_html=True)
    
    try:
        trending = get_trending_movies()
        cols = st.columns(6)
        for i, movie in enumerate(trending):
            with cols[i]:
                render_movie_card(movie, f"trend_{i}")
    except Exception as e:
        st.error(f"Backend offline. Start FastAPI server. Error: {e}")

elif selected == "Discover":
    st.markdown("### Search Movies")
    q = st.text_input("", placeholder="e.g. Inception", label_visibility="collapsed")
    if q:
        st.markdown("<br>", unsafe_allow_html=True)
        results = requests.get(f"{API_URL}/movies/search?q={q}").json()
        if results:
            cols = st.columns(4)
            for idx, movie in enumerate(results):
                with cols[idx % 4]:
                    with st.container(border=True):
                        render_movie_card(movie, f"disc_{idx}")
        else:
            st.info("No movies found.")

elif selected == "My List":
    st.header("My List")
    tabs = st.tabs(["⭐ Favourite", "📅 Plan to Watch", "✅ Completed"])
    
    ratings = requests.get(f"{API_URL}/ratings/{st.session_state.user_id}").json()
    df = pd.DataFrame(ratings) if ratings else pd.DataFrame()
    
    with tabs[0]:
        st.subheader("Favourite Movies")
        if not df.empty:
            favs = df[df['rating'] >= 4.0]
            if not favs.empty:
                st.dataframe(favs[['title', 'rating', 'timestamp']], use_container_width=True)
            else:
                st.info("No favourites yet. Rate movies 4 stars or higher to see them here!")
        else:
            st.info("No favourites yet.")
            
    with tabs[1]:
        st.subheader("Plan to Watch")
        try:
            watchlist = requests.get(f"{API_URL}/watchlist/{st.session_state.user_id}").json()
            w_df = pd.DataFrame(watchlist) if watchlist else pd.DataFrame()
            if not w_df.empty:
                st.dataframe(w_df[['title', 'genres', 'timestamp']], use_container_width=True)
            else:
                st.info("Your Plan to Watch list is empty. Add some movies from the browse page!")
        except:
            st.info("Feature coming soon! You will be able to add movies to your Plan to Watch list here.")
        
    with tabs[2]:
        st.subheader("Completed Movies")
        if not df.empty:
            st.dataframe(df[['title', 'rating', 'timestamp']], use_container_width=True)
        else:
            st.info("You haven't completed (rated) any movies yet.")

elif selected == "Top Picks":
    st.markdown("### Your Top Picks")
    algo = st.selectbox("Engine", ["svd", "knn", "baseline"])
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with st.spinner("Generating personalized recommendations..."):
            recs = get_recommendations_cached(st.session_state.user_id, algo)
        
        cols = st.columns(4)
        for idx, movie in enumerate(recs):
            with cols[idx % 4]:
                with st.container(border=True):
                    render_movie_card(movie, f"top_{idx}")
        
        st.write("---")
        st.markdown("### AI Mood Re-ranker")
        mood = st.text_input("What are you in the mood for?", placeholder="e.g. late night thriller")
        if st.button("Re-rank by Mood") and mood:
            with st.spinner("AI is re-ranking based on your mood..."):
                res = requests.post(f"{API_URL}/ai/rerank", json={"movies": [m['title'] for m in recs], "mood": mood}).json()
                st.success(res["result"])
    except Exception as e:
        st.error(f"Failed to load recommendations. Please make sure you have rated some movies and the models are trained.")
