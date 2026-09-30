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
    
st.set_page_config(page_title="MovieMatch", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for a Stunning UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Card Design */
    .movie-card {
        background: var(--secondary-background-color);
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        padding: 16px;
        margin-bottom: 10px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .movie-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.3);
        border-color: var(--primary-color);
    }
    .movie-poster {
        border-radius: 16px;
        width: 100%;
        object-fit: cover;
        aspect-ratio: 2/3;
        margin-bottom: 16px;
    }
    .movie-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .movie-genre {
        font-size: 0.8rem;
        color: var(--text-color);
        opacity: 0.7;
        margin-bottom: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .rating-badge {
        color: #f59e0b;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    
    /* Button Styling */
    div.stButton > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 0.6rem !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #2563eb !important;
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-2px);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def render_movie_card(title, genres, rating=None):
    colors = ["ef4444", "3b82f6", "10b981", "f59e0b", "8b5cf6", "ec4899"]
    bg_color = colors[len(title) % len(colors)]
    poster_letter = urllib.parse.quote(title[0].upper()) if title else "M"
    poster_url = f"https://placehold.co/400x600/{bg_color}/ffffff?text={poster_letter}"
    
    rating_html = f"<div class='rating-badge'>★ {rating:.1f} / 5.0</div>" if rating is not None else ""
    
    html = f"""
    <div class="movie-card">
        <img src="{poster_url}" class="movie-poster">
        <div class="movie-title" title="{title}">{title}</div>
        <div class="movie-genre" title="{genres}">{genres}</div>
        {rating_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Load Data & Model ---
@st.cache_data
def load_data():
    return pd.read_csv('movies.csv')

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

# --- UI Layout ---

st.sidebar.image("https://placehold.co/400x150/1e293b/ffffff?text=MovieMatch", use_container_width=True)
st.sidebar.write("---")

if 'username' not in st.session_state:
    st.session_state.username = None

username_input = st.sidebar.text_input("👤 Enter Username:")
if st.sidebar.button("Login / Register"):
    if username_input:
        st.session_state.username = username_input
        st.session_state.user_id = get_or_create_user(username_input)
        st.sidebar.success(f"Welcome, {username_input}!")
    else:
        st.sidebar.error("Please enter a username.")

page = st.sidebar.radio("Navigation", ["Home", "Browse Movies", "My Ratings", "Recommendations"])

if page == "Home":
    st.title("🎬 Welcome to MovieMatch")
    st.write("Discover your next favorite movie with personalized AI recommendations.")
    st.write("⬅️ Use the sidebar to log in and start exploring!")

elif page == "Browse Movies":
    st.title("🍿 Browse & Rate Movies")
    if not st.session_state.username:
        st.warning("Please login from the sidebar first.")
    else:
        search_query = st.text_input("🔍 Search for a movie (e.g., 'Toy Story'):")
        if search_query:
            results = movies_df[movies_df['title'].str.contains(search_query, case=False, na=False)].head(12)
            if results.empty:
                st.write("No movies found.")
            else:
                cols = st.columns(4)
                for idx, row in results.reset_index().iterrows():
                    col = cols[idx % 4]
                    with col:
                        render_movie_card(row['title'], row['genres'])
                        with st.expander("Rate & AI Details"):
                            ai_key = f"ai_{row['movieId']}"
                            if ai_key not in st.session_state:
                                if not GENAI_API_KEY:
                                    st.error("Gemini API key missing.")
                                else:
                                    try:
                                        gemini_model = genai.GenerativeModel('gemini-flash-latest')
                                        prompt = f"Provide a very short 2-sentence synopsis for the movie '{row['title']}'."
                                        st.session_state[ai_key] = gemini_model.generate_content(prompt).text
                                    except Exception as e:
                                        st.session_state[ai_key] = "AI synopsis unavailable (Rate limit or error)."
                            
                            st.info(st.session_state.get(ai_key, ""))
                                
                            st.write("---")
                            rating = st.slider("Stars", 1.0, 5.0, 3.0, 0.5, key=f"rate_{row['movieId']}")
                            if st.button("Submit Rating", key=f"btn_{row['movieId']}"):
                                add_rating(st.session_state.user_id, row['movieId'], rating)
                                st.success("Saved!")

elif page == "My Ratings":
    st.title("⭐ My Ratings")
    if not st.session_state.username:
        st.warning("Please login from the sidebar first.")
    else:
        user_ratings = get_user_ratings(st.session_state.user_id)
        if user_ratings.empty:
            st.info("You haven't rated any movies yet.")
        else:
            st.dataframe(user_ratings[['title', 'rating', 'timestamp']], use_container_width=True)

elif page == "Recommendations":
    st.title("✨ For You")
    if not st.session_state.username:
        st.warning("Please login from the sidebar first.")
    else:
        st.write("Top picks tailored just for you.")
        
        algo_choice = st.selectbox(
            "Select Recommendation Algorithm:",
            ("SVD (Advanced Latent Factors)", "KNN (Collaborative Filtering)", "Baseline (Statistical Average)")
        )
        
        model_name_map = {
            "SVD (Advanced Latent Factors)": "svd",
            "KNN (Collaborative Filtering)": "knn",
            "Baseline (Statistical Average)": "baseline"
        }
        
        selected_algo = model_name_map[algo_choice]
        model = load_model(selected_algo)
        
        if not model:
            st.error(f"{algo_choice} model not trained. Please run train_model.py first.")
        else:
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
                col = cols[idx % 4]
                with col:
                    render_movie_card(title, genres, rating)
                    with st.expander("AI Details"):
                        ai_key = f"rec_ai_{idx}"
                        if ai_key not in st.session_state:
                            if not GENAI_API_KEY:
                                st.error("Gemini API key missing.")
                            else:
                                try:
                                    gemini_model = genai.GenerativeModel('gemini-flash-latest')
                                    prompt = f"Provide a very short 2-sentence synopsis for the movie '{title}'."
                                    st.session_state[ai_key] = gemini_model.generate_content(prompt).text
                                except Exception as e:
                                    st.session_state[ai_key] = "AI synopsis unavailable (Rate limit or error)."
                        
                        st.info(st.session_state.get(ai_key, ""))
            
            st.write("---")
            st.subheader("🧠 Ask Gemini")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Explain these recommendations"):
                    if not GENAI_API_KEY: st.error("Gemini API key missing.")
                    else:
                        with st.spinner("Gemini is analyzing..."):
                            gemini_model = genai.GenerativeModel('gemini-flash-latest')
                            titles = ", ".join([t[0] for t in top_12])
                            prompt = f"I am a user of a movie recommendation system. The system recommended these movies: {titles}. Explain in one engaging paragraph why these might be grouped together."
                            st.info(gemini_model.generate_content(prompt).text)
                            
            with col2:
                mood = st.text_input("What's your mood?", placeholder="e.g., I want to laugh")
                if st.button("Re-rank by Mood"):
                    if not GENAI_API_KEY: st.error("Gemini API key missing.")
                    elif not mood: st.error("Please enter a mood.")
                    else:
                        with st.spinner("Gemini is re-ranking..."):
                            gemini_model = genai.GenerativeModel('gemini-flash-latest')
                            titles = [t[0] for t in top_12]
                            prompt = f"Given these 12 movies: {titles}. User's mood: '{mood}'. Re-order to best match the mood. Return a numbered list."
                            st.success(gemini_model.generate_content(prompt).text)
