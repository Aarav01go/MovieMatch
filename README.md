# 🎬 MovieMatch: Next-Gen AI Recommendation Engine

MovieMatch is a full-fledged, premium movie discovery and recommendation platform. Featuring a completely new, cinematic React frontend inspired by leading streaming platforms, it dynamically blends traditional Machine Learning collaborative filtering algorithms with next-generation LLM metadata generation and mood-based discovery.

## ✨ Features

- **React Netflix-Style UI**: A beautiful, dark-themed, highly visual interface built with React, Vite, and Tailwind CSS. Features horizontal carousels, immersive hero banners, and slick hover interactions.
- **Multiple ML Engines**: Choose real-time between SVD (Matrix Factorization), KNN (Item-based Collaborative Filtering), and Statistical Baseline.
- **Local Poster Caching**: A dedicated background service that fetches high-quality movie posters via OMDB and caches them locally for lightning-fast, API-independent loads. Robust frontend fallbacks ensure there is *never* a broken image.
- **AI Fallback & Discovery**: Search for a movie that doesn't exist in the local dataset? The OpenRouter LLM dynamically constructs its metadata, injects it into the SQLite database, and serves it instantly.
- **AI Mood Re-ranker**: Filter your personalized Top-12 recommendations using natural language (e.g., "I'm in the mood for a late-night thriller").
- **AI Synopses**: Dynamically generated, captivating 2-sentence summaries for thousands of movies.

## 🏗 Architecture

The project is structured into a decoupled, production-style architecture:

* **Frontend**: React + Vite (`frontend/` running on 5173)
* **Backend**: FastAPI (`backend/main.py` running on 8000)
* **Database**: SQLite (via SQLAlchemy, abstracted for easy PostgreSQL migration)
* **ML Layer**: Pre-trained `scikit-surprise` models loaded via a dedicated `RecommendationService`.
* **AI Layer**: `ai_service.py` securely managing LLM calls to OpenRouter.

## 🛠 Tech Stack

- **Frontend**: React, React Router, Tailwind CSS, Lucide React, Axios
- **Backend**: FastAPI, SQLAlchemy, Pydantic, scikit-surprise
- **Metadata**: OMDB API

## 🚀 Installation & Setup

1. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_KEY=your_key_here
   OMDB_API_KEY=thewdb
   DATABASE_URL=sqlite:///backend/data/moviematch.db
   ```

2. **Start the FastAPI Backend**
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Start the React Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Bootstrap Metadata & Posters (Optional)**
   Run the caching script to fetch and store high-res posters locally for a smooth UI experience.
   ```bash
   python scripts/bootstrap_movie_metadata.py --limit 100
   ```

## 🧪 Testing
Run the automated backend test suite:
```bash
python -m pytest backend/tests/test_endpoints.py
```
