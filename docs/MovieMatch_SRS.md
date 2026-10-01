# Software Requirements Specification (SRS)
## Project Name: MovieMatch
**Version:** 2.0  
**Date:** October 2026

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the Software Requirements Specification (SRS) for MovieMatch, a next-generation AI and Machine Learning-powered movie discovery platform. This document outlines the functional and non-functional requirements, system architecture, and product constraints.

### 1.2 Scope
MovieMatch aims to solve the problem of decision fatigue in modern streaming platforms. Instead of presenting random static lists, MovieMatch utilizes Machine Learning (Collaborative Filtering) and Generative AI (LLMs) to actively predict user preferences, answer conversational queries, and merge taste profiles across users. The platform supports a catalog of over 80,000 modern global movies.

---

## 2. Overall Description

### 2.1 Product Perspective
MovieMatch operates as an independent web application utilizing a modern Client-Server architecture. The frontend is a responsive React Single Page Application (SPA), while the backend is a Python-based FastAPI server managing SQLite operations, `scikit-surprise` ML models, and asynchronous background ETL daemons for metadata caching.

### 2.2 User Classes and Characteristics
* **Standard User:** Can browse movies, interact with the AI assistant, rate movies, add movies to a watchlist, and use the Matchmaker feature.
* **System Administrator / Background Daemon:** Automated backend scripts responsible for downloading massive IMDB datasets, fetching OMDB posters, and retraining ML models autonomously.

### 2.3 Operating Environment
* **Client:** Any modern web browser (Chrome, Firefox, Safari) running JavaScript.
* **Server:** Linux/Unix or Windows environment with Python 3.10+ and Node.js.
* **Database:** SQLite (scalable up to hundreds of thousands of records).

---

## 3. System Features (Functional Requirements)

### 3.1 Authentication & User Profiles
* **FR-1.1:** The system shall allow users to log in using a unique username.
* **FR-1.2:** The system shall track individual user rating histories and watchlist additions.

### 3.2 Machine Learning Recommendation Engine
* **FR-2.1:** The system shall employ Singular Value Decomposition (SVD) and K-Nearest Neighbors (KNN) algorithms to generate personalized movie predictions based on historical user interactions.
* **FR-2.2:** The system shall dynamically extract and recommend sequels and prequels (franchise mapping) for any selected movie based on intelligent title parsing.

### 3.3 The "Date Night" Matchmaker
* **FR-3.1:** The system shall allow a user to input a second user's profile ID.
* **FR-3.2:** The backend shall calculate the intersection of both users' predicted ratings using a Harmonic Mean algorithm and output mutual recommendations that satisfy both taste profiles.

### 3.4 Conversational Generative AI
* **FR-4.1:** The system shall provide a floating chat assistant powered by a Large Language Model (OpenRouter API).
* **FR-4.2:** The AI shall interpret natural language queries (e.g., "I want a classic sci-fi movie"), map the response to the internal SQLite database, and return a clickable movie card.
* **FR-4.3:** The AI shall dynamically generate a personalized welcome message based on the user's highest-rated movies upon login.

### 3.5 Massive Catalog Management (ETL)
* **FR-5.1:** The system shall support a database of 80,000+ global blockbuster movies (Hollywood, Bollywood, Tollywood).
* **FR-5.2:** Background daemons shall autonomously query the OMDB API to download and locally cache high-resolution artwork to `static/posters/` to prevent broken images.

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
* **NFR-1:** API endpoints fetching basic movie data must return a response in under 200ms.
* **NFR-2:** The frontend UI must implement horizontal scrolling rails with lazy-loaded images to maintain 60FPS scrolling performance.
* **NFR-3:** Images must be served from the local cache rather than making direct API calls to OMDB on every client load.

### 4.2 UI / UX Requirements
* **NFR-4:** The application must utilize a dark, cinematic UI theme heavily inspired by premium streaming platforms (e.g., Netflix).
* **NFR-5:** The platform must be fully responsive and optimized for both desktop and mobile viewing.

### 4.3 Reliability & Availability
* **NFR-6:** If the OpenRouter LLM API goes down, the platform must gracefully degrade and continue providing ML-based collaborative filtering recommendations.
* **NFR-7:** If OMDB fails to return a poster, the frontend must render a clean fallback gradient box containing the movie title without throwing a fatal error.

---

## 5. System Architecture & Tech Stack
* **Frontend:** React, Vite, Tailwind CSS (v4)
* **Backend:** FastAPI, Python, Uvicorn
* **Database / ORM:** SQLite, SQLAlchemy
* **Machine Learning:** `scikit-surprise` (SVD, KNNBaseline, ALS)
* **Generative AI:** OpenRouter HTTP Client
* **Data Sources:** MovieLens (Ratings), IMDb Datasets (Raw Movie Records), OMDB API (Metadata/Posters)
