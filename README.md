# 🎬 MovieMatch: Next-Gen AI Recommendation Engine

MovieMatch is a full-stack, AI-powered movie recommendation platform built with a premium cinematic UI. Originally derived from an academic machine learning research project, it has been completely restructured into a modern, production-ready web application featuring multiple collaborative filtering algorithms and deep integration with Google's Gemini AI.

## ✨ Core Features

### 🧠 Advanced Recommendation Engines
- **Multi-Algorithm Architecture**: Choose your preferred engine in real-time from the UI:
  - **SVD (Singular Value Decomposition)**: Advanced matrix factorization.
  - **KNN (K-Nearest Neighbors)**: Item/User-based collaborative filtering.
  - **Statistical Baseline**: Weighted average algorithms.
- **Pre-trained Performance**: Models are pre-trained on the MovieLens dataset for instant inference.

### 🤖 Gemini AI Integration
- **Dynamic Dataset Expansion**: If you search for a movie that doesn't exist in the local dataset, the backend seamlessly pings Gemini to fetch the real movie details, dynamically appends it to the dataset, and makes it rateable instantly.
- **AI Synopses**: Generates captivating, 2-sentence synopses on-the-fly for any movie.
- **The AI Director**: Asks Gemini to analyze your Top-12 recommendations and explain *why* the algorithm grouped those specific movies together based on your taste profile.
- **Mood Re-ranker**: Tell the AI your current mood (e.g., "I want to laugh" or "late night thriller"), and it will instantly re-order your personalized recommendations to perfectly match your vibe.

### 🎨 Premium Cinematic UI
- **Netflix-Style Frontend**: Built entirely in native Streamlit, featuring a full CSS overhaul.
- **Top Navigation Bar**: Seamless multi-page routing (`Home`, `Discover`, `My List`, `Top Picks`) using `streamlit-option-menu`.
- **Glassmorphism & 3D Cards**: Immersive dark-mode gradients, frosted glass sidebars, and floating movie posters.

### 💾 Persistent User Profiles
- Integrated **SQLite Database** (`moviematch.db`).
- Create a profile, search movies, and save star ratings. The machine learning models use your saved ratings to generate the `Top Picks`.

---

## 🏗️ Architecture

The project has been refactored into a decoupled Full-Stack architecture:

* **`/backend`**: A blazingly fast **FastAPI** server running on port `8000`. It handles all heavy lifting, loads the `.pkl` machine learning models, interacts with SQLite, and securely communicates with the Gemini API.
* **`/frontend`**: A **Streamlit** application running on port `8501`. It acts strictly as a UI layer, communicating with the backend via REST HTTP requests.
* **`/Code`**: The original academic Jupyter Notebooks containing the mathematical research and model evaluation.

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
pip install fastapi uvicorn streamlit streamlit-option-menu pydantic pandas google-generativeai scikit-surprise
```

### 2. Add API Keys
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Start the Backend (FastAPI)
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Start the Frontend (Streamlit)
Open a new terminal and run:
```bash
streamlit run frontend/app.py
```

### 5. Access the App
Navigate to `http://localhost:8501` in your browser!

---
*Developed by Aarav.*
