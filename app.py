import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import sqlite3
import pickle
import urllib.parse
from dotenv import load_dotenv

# --- Configuration & Setup ---
load_dotenv()
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    
st.set_page_config(page_title="MovieMatch Ultra", layout="wide", initial_sidebar_state="expanded")

# --- Next-Gen CSS for Premium UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Deep Cinematic Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1a24 0%, #09090b 100%) !important;
        color: #f4f4f5 !important;
    }
    
    header { visibility: hidden; }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 9, 11, 0.75) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Netflix-style Hero Banner */
    .hero-banner {
        width: 100%;
        height: 450px;
        background: linear-gradient(to right, rgba(9,9,11,1) 0%, rgba(9,9,11,0.2) 50%, rgba(9,9,11,1) 100%),
                    url('https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070') no-repeat center center;
        background-size: cover;
        border-radius: 20px;
        position: relative;
        margin-bottom: 50px;
        display: flex;
        align-items: flex-end;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    .hero-content {
        padding: 50px;
        z-index: 2;
        width: 100%;
        background: linear-gradient(to top, #09090b 10%, transparent);
        border-radius: 0 0 20px 20px;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
        line-height: 1;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #a1a1aa;
        margin-top: 15px;
        max-width: 600px;
    }
    
    /* Premium 3D Movie Cards */
    .movie-card {
        background: #18181b;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 25px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(255, 255, 255, 0.03);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .movie-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0,0,0,0.6);
        border-color: #e50914;
    }
    .movie-poster {
        width: 100%;
        aspect-ratio: 2/3;
        object-fit: cover;
        border-bottom: 3px solid #e50914;
    }
    .movie-info {
        padding: 16px;
    }
    .movie-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f4f4f5;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .movie-genre {
        font-size: 0.8rem;
        color: #71717a;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .rating-badge {
        display: inline-block;
        background: rgba(229, 9, 20, 0.1);
        color: #e50914;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-top: 10px;
        border: 1px solid rgba(229, 9, 20, 0.3);
    }
    
    /* Cinematic Buttons */
    div.stButton > button {
        background: #e50914 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background: #f6121d !important;
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.4) !important;
        transform: scale(1.02);
    }
    
    /* Custom Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #18181b !important;
        border: 1px solid #27272a !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #e50914 !important;
        box-shadow: 0 0 0 1px #e50914 !important;
    }
    
    hr {
        border-color: #27272a;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def render_movie_card(title, genres, rating=None):
    colors = ["18181b", "27272a", "09090b"]
    bg_color = colors[len(title) % len(colors)]
    poster_letter = urllib.parse.quote(title[0].upper()) if title else "M"
    # Using Unsplash cinematic placeholders instead of solid colors when possible
    poster_url = f"https://placehold.co/400x600/{bg_color}/e50914?text={poster_letter}&font=montserrat"
    
    rating_html = f"<div class='rating-badge'>⭐ {rating:.1f} Match</div>" if rating is not None else ""
    
    html = f"""
    <div class="movie-card">
        <img src="{poster_url}" class="movie-poster">
        <div class="movie-info">
            <div class="movie-title" title="{title}">{title}</div>
            <div class="movie-genre" title="{genres}">{genres.replace('|', ' • ')}</div>
            {rating_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Load Data & Model ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv('movies.csv')
    except:
        return pd.DataFrame(columns=['movieId', 'title', 'genres'])

@st.cache_resource
def load_model(model_name="svd"):
    try:
        with open(f'{model_name}_model.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

movies_df = load_data()

# --- Database Helpers ---
DB_PATH = 'moviematch.db'
def get_db_connection(): return sqlite3.connect(DB_PATH)

def get_or_create_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row: user_id = row[0]
    else:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        user_id = cursor.lastrowid
    conn.close()
    return user_id

def add_rating(user_id, movie_id, rating):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)", (user_id, movie_id, rating))
    conn.commit()
    conn.close()
    
def get_user_ratings(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, rating, timestamp FROM ratings WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return pd.DataFrame()
    ratings_df = pd.DataFrame(rows, columns=['movieId', 'rating', 'timestamp'])
    return pd.merge(ratings_df, movies_df, on='movieId', how='left')

# --- Sidebar UI ---
st.sidebar.markdown("<h1 style='color: #e50914; font-weight: 900; font-size: 2rem;'>MOVIE<span style='color:white'>MATCH</span></h1>", unsafe_allow_html=True)
st.sidebar.write("---")

if 'username' not in st.session_state:
    st.session_state.username = None

username_input = st.sidebar.text_input("Profile Name", placeholder="Enter to login...")
if st.sidebar.button("Access Profile"):
    if username_input:
        st.session_state.username = username_input
        st.session_state.user_id = get_or_create_user(username_input)
        st.sidebar.success(f"Welcome back, {username_input}")
    else:
        st.sidebar.error("Profile name required.")

st.sidebar.write("---")
page = st.sidebar.radio("Menu", ["🏠 Home", "🔍 Discover", "⭐ My List", "🍿 Top Picks"])

# --- Main Pages ---

if page == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-content">
            <h1 class="hero-title">Unlimited movies,<br>tailored for you.</h1>
            <p class="hero-subtitle">Experience our next-generation AI recommendation engine. Log in from the menu to build your profile, rate movies, and unlock personalized cinematic experiences powered by Google Gemini and advanced Collaborative Filtering.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔥 Trending Now")
    if not movies_df.empty:
        cols = st.columns(6)
        trending = movies_df.sample(6, random_state=42)
        for idx, row in trending.reset_index().iterrows():
            with cols[idx]:
                render_movie_card(row['title'], row['genres'])

elif page == "🔍 Discover":
    st.markdown("<h1 style='font-weight: 900;'>Discover Movies</h1>", unsafe_allow_html=True)
    if not st.session_state.username:
        st.warning("Please access your profile from the sidebar first.")
    else:
        search_query = st.text_input("", placeholder="Search titles, genres, or keywords...")
        if search_query:
            results = movies_df[movies_df['title'].str.contains(search_query, case=False, na=False)].head(12)
            if results.empty:
                st.write("No matches found.")
            else:
                st.write("---")
                cols = st.columns(4)
                for idx, row in results.reset_index().iterrows():
                    col = cols[idx % 4]
                    with col:
                        render_movie_card(row['title'], row['genres'])
                        with st.expander("RATE & DETAILS"):
                            ai_key = f"ai_{row['movieId']}"
                            if ai_key not in st.session_state:
                                if not GENAI_API_KEY:
                                    st.error("API key missing.")
                                else:
                                    try:
                                        gemini_model = genai.GenerativeModel('gemini-flash-latest')
                                        st.session_state[ai_key] = gemini_model.generate_content(f"Write a 2-sentence captivating synopsis for '{row['title']}'.").text
                                    except Exception:
                                        st.session_state[ai_key] = "Synopsis unavailable."
                            st.caption(st.session_state.get(ai_key, ""))
                                
                            rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.5, key=f"rate_{row['movieId']}")
                            if st.button("SAVE RATING", key=f"btn_{row['movieId']}"):
                                add_rating(st.session_state.user_id, row['movieId'], rating)
                                st.success("Added to My List!")

elif page == "⭐ My List":
    st.markdown("<h1 style='font-weight: 900;'>My List</h1>", unsafe_allow_html=True)
    if not st.session_state.username:
        st.warning("Please access your profile from the sidebar first.")
    else:
        user_ratings = get_user_ratings(st.session_state.user_id)
        if user_ratings.empty:
            st.info("Your list is empty. Go to Discover to add some movies!")
        else:
            st.dataframe(user_ratings[['title', 'rating', 'timestamp']], use_container_width=True, hide_index=True)

elif page == "🍿 Top Picks":
    st.markdown("<h1 style='font-weight: 900;'>Top Picks For You</h1>", unsafe_allow_html=True)
    if not st.session_state.username:
        st.warning("Please access your profile from the sidebar first.")
    else:
        algo_choice = st.selectbox(
            "Engine Architecture",
            ("SVD Matrix Factorization", "KNN Collaborative Filtering", "Baseline Averages")
        )
        
        model_name_map = {
            "SVD Matrix Factorization": "svd",
            "KNN Collaborative Filtering": "knn",
            "Baseline Averages": "baseline"
        }
        
        model = load_model(model_name_map[algo_choice])
        
        if not model:
            st.error(f"The {algo_choice} engine is currently offline.")
        else:
            st.write("---")
            sample_movies = movies_df.sample(200, random_state=42)
            predictions = []
            for _, row in sample_movies.iterrows():
                pred = model.predict(uid=st.session_state.user_id, iid=row['movieId'])
                predictions.append((row['title'], row['genres'], pred.est))
                
            predictions.sort(key=lambda x: x[2], reverse=True)
            top_12 = predictions[:12]
            
            cols = st.columns(4)
            for idx, movie in enumerate(top_12):
                title, genres, rating = movie
                with cols[idx % 4]:
                    render_movie_card(title, genres, rating)
                    with st.expander("VIEW SYNOPSIS"):
                        ai_key = f"rec_ai_{idx}"
                        if ai_key not in st.session_state:
                            if not GENAI_API_KEY:
                                st.error("API key missing.")
                            else:
                                try:
                                    gemini_model = genai.GenerativeModel('gemini-flash-latest')
                                    st.session_state[ai_key] = gemini_model.generate_content(f"Write a 2-sentence captivating synopsis for '{title}'.").text
                                except Exception:
                                    st.session_state[ai_key] = "Synopsis unavailable."
                        st.caption(st.session_state.get(ai_key, ""))
            
            st.write("---")
            st.markdown("### 🧠 AI Director")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ANALYZE MY TASTE"):
                    if not GENAI_API_KEY: st.error("API key missing.")
                    else:
                        with st.spinner("Analyzing..."):
                            gemini_model = genai.GenerativeModel('gemini-flash-latest')
                            titles = ", ".join([t[0] for t in top_12])
                            prompt = f"The system recommended: {titles}. Explain in one engaging paragraph why these are grouped together."
                            st.info(gemini_model.generate_content(prompt).text)
                            
            with col2:
                mood = st.text_input("", placeholder="Tell the AI what you're in the mood for...")
                if st.button("RE-RANK CURATION"):
                    if not GENAI_API_KEY: st.error("API key missing.")
                    elif not mood: st.error("Please enter a mood.")
                    else:
                        with st.spinner("Curating..."):
                            gemini_model = genai.GenerativeModel('gemini-flash-latest')
                            titles = [t[0] for t in top_12]
                            prompt = f"Movies: {titles}. User's mood: '{mood}'. Re-order to best match. Return a numbered list."
                            st.success(gemini_model.generate_content(prompt).text)
