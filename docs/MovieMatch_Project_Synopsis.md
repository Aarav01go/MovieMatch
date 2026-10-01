 # MovieMatch: Next-Gen AI & ML Movie Discovery Platform

## 1. Project Overview
MovieMatch is an enterprise-grade, AI-powered movie discovery and recommendation platform. It transcends traditional CRUD applications by integrating **Machine Learning (Collaborative Filtering)** for personalized recommendations, **Generative AI** for conversational movie discovery, and a massive **80,000+ movie database** sourced from MovieLens and IMDb.

The frontend is a highly polished, Netflix-inspired React SPA (Single Page Application) designed for deep cinematic immersion, fully replacing the project's original basic Streamlit interface.

## 2. Technology Stack
* **Frontend:** React, Vite, JavaScript, Tailwind CSS (v4), React Router, Lucide-React.
* **Backend:** FastAPI, Python, SQLAlchemy, SQLite.
* **Machine Learning:** `scikit-surprise` (SVD, KNNBaseline).
* **Generative AI:** OpenRouter API (LLM integration).
* **Data Engineering:** Custom Python ETL scripts, OMDB API for artwork caching.

## 3. Core Features & System Architecture

### A. The Recommendation Engine (Machine Learning)
The platform does not rely on simple keyword matching. It utilizes a **Collaborative Filtering** matrix powered by Singular Value Decomposition (SVD). 
* **Matrix Factorization:** The ML model (`svd_model.pkl`) is trained on hundreds of thousands of simulated and real user-rating interactions.
* **Date Night Matchmaker:** A custom mathematical algorithm that takes two distinct user profiles, runs `.predict()` for both across the catalog, and uses a Harmonic Mean to recommend a movie that perfectly satisfies both users.

### B. Massive Data Pipeline (ETL)
To ensure the catalog felt like a modern streaming giant, custom ETL (Extract, Transform, Load) daemons were built:
* **IMDb Integration:** Parsed and injected over 80,000 modern cinematic releases (2005–2026) from the massive IMDb Non-Commercial dataset.
* **Curated Global Hits:** Specifically integrated the Marvel Cinematic Universe (MCU) and all-time blockbusters from Bollywood and Tollywood.
* **Artwork Caching Daemon:** Background Python workers that automatically hit the OMDB API to download and locally cache high-resolution posters to `static/posters/`, ensuring zero broken images.

### C. Generative AI Integrations
* **Floating AI Assistant:** A React chat component that uses natural language processing. Users can say "I want a classic sci-fi movie," and the LLM maps the psychological request directly to a `movieId` in the local SQLite database.
* **Dynamic Synopsis Generation:** If a movie lacks a description, the OpenRouter LLM dynamically generates a captivating, 2-sentence cinematic synopsis on the fly.
* **Personalized AI Welcome:** The AI analyzes a user's specific highest-rated movies upon login and generates a completely personalized greeting and recommendation.

### D. The Cinematic User Interface
* Completely rebuilt from scratch using React and Tailwind CSS.
* Features a massive dynamic Hero banner with gradient overlays, responsive horizontal scrolling carousels (`MovieRail`), hover-scale animations, and "The Collection" rails for franchise mapping (e.g., automatically finding sequels).

---

## 4. Source Code (`src`) Directory Structure
The architecture adheres to strict modularity and separation of concerns.

```text
MovieMatch/
│
├── backend/                       # REST API & Machine Learning Layer
│   ├── main.py                    # FastAPI application entry point & exception handlers
│   ├── database.py                # SQLAlchemy SQLite engine configuration
│   ├── config.py                  # Environment variable management
│   ├── models/                    # Database schemas (Movie, User, Rating, Watchlist)
│   ├── schemas/                   # Pydantic validation models for request/response
│   ├── routes/                    # API Endpoints (movies.py, users.py, ai.py, etc.)
│   ├── services/                  # Core Business Logic
│   │   ├── ai_service.py          # OpenRouter LLM prompt engineering and parsing
│   │   ├── movie_service.py       # Advanced DB querying (Sequels, Marvel, Trending)
│   │   ├── recommendation_service # scikit-surprise model loading and predictions
│   │   └── image_service.py       # OMDB Poster downloading and caching
│   ├── data/                      # Raw datasets and SQLite database (moviematch.db)
│   └── models_ml/                 # Trained neural weights (svd_model.pkl)
│
├── frontend/                      # React SPA Presentation Layer
│   ├── src/
│   │   ├── api/                   # Axios interceptors and client configuration
│   │   ├── components/            # Reusable UI (Navbar, MovieRail, MovieCard, FloatingAI)
│   │   ├── context/               # Global React State (AuthContext)
│   │   ├── pages/                 # Full Views (Home, Login, MovieDetails, Matchmaker)
│   │   ├── App.jsx                # React Router DOM configuration
│   │   └── index.css              # Tailwind v4 theme definitions
│   └── package.json               # Node.js dependencies
│
├── scripts/                       # Autonomous Background Daemons (ETL)
│   ├── bootstrap_movie_metadata.py# Base OMDB artwork downloader
│   ├── inject_imdb_massive.py     # Parses 200MB TSV archives to inject 80k+ movies
│   ├── inject_global_hits.py      # Hardcodes and injects MCU/Bollywood hits
│   └── train_models.py            # Generates synthetic ratings and retrains SVD/KNN
│
├── static/                        # Locally cached assets (Posters, Backdrops)
└── docs/                          # Project documentation and academic reports
```
