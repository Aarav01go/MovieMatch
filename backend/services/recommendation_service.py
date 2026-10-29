import pickle
import os
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from models.movie import Movie


class RecommendationService:
    def __init__(self):
        self.models = {}
        self._load_models()

    def _load_models(self):
        """
        Try both path layouts:
          1. backend/models_ml/  (preferred — separate from ORM models)
          2. backend/models/     (legacy location)
        KNN is intentionally excluded from deployment (725 MB) —
        it degrades gracefully to SVD if requested.
        """
        for algo in ["svd", "baseline"]:
            for base in ["backend/models_ml", "backend/models"]:
                path = f"{base}/{algo}_model.pkl"
                if os.path.exists(path):
                    try:
                        with open(path, "rb") as f:
                            self.models[algo] = pickle.load(f)
                        print(f"[ML] Loaded {algo} from {path}")
                        break
                    except Exception as e:
                        print(f"[ML] Failed to load {algo}: {e}")
            else:
                self.models.setdefault(algo, None)

        # KNN is too large (725 MB) for free hosting — skip silently
        self.models["knn"] = None
        print("[ML] KNN skipped (too large for deployment — SVD/Baseline available)")

    def _get_model(self, algo: str):
        """Return the requested model, falling back to SVD if unavailable."""
        model = self.models.get(algo)
        if model is None and algo == "knn":
            # Graceful degradation: serve SVD instead of crashing
            model = self.models.get("svd")
        if model is None:
            raise ValueError(f"No recommendation model available (requested: {algo})")
        return model

    def get_recommendations(self, user_id: int, algo: str, db: Session, limit: int = 12):
        model = self._get_model(algo)

        sample_movies = db.query(Movie).order_by(func.random()).limit(300).all()
        predictions = []
        for m in sample_movies:
            try:
                pred = model.predict(uid=user_id, iid=m.movie_id)
                display_algo = algo if self.models.get(algo) else "svd"
                predictions.append({
                    "movieId": m.movie_id,
                    "title": m.title,
                    "genres": m.genres,
                    "poster_url": m.poster_url,
                    "score": pred.est,
                    "reason": f"Matches your taste profile ({display_algo.upper()})",
                })
            except Exception:
                continue

        predictions.sort(key=lambda x: x["score"], reverse=True)
        return predictions[:limit]

    def get_mutual_recommendations(
        self,
        user1_id: int,
        user2_id: int,
        db: Session,
        algo: str = "svd",
        limit: int = 12,
    ):
        model = self._get_model(algo)

        sample_movies = (
            db.query(Movie)
            .filter(Movie.poster_url.isnot(None))
            .order_by(func.random())
            .limit(400)
            .all()
        )
        predictions = []
        for m in sample_movies:
            try:
                pred1 = model.predict(uid=user1_id, iid=m.movie_id)
                pred2 = model.predict(uid=user2_id, iid=m.movie_id)
                combined = (
                    (2 * pred1.est * pred2.est) / (pred1.est + pred2.est)
                    if (pred1.est + pred2.est) > 0
                    else 0
                )
                predictions.append({
                    "movieId": m.movie_id,
                    "title": m.title,
                    "genres": m.genres,
                    "poster_url": m.poster_url,
                    "score": round(combined, 2),
                    "user1_score": round(pred1.est, 2),
                    "user2_score": round(pred2.est, 2),
                    "reason": "Great match for both of you!",
                })
            except Exception:
                continue

        predictions.sort(key=lambda x: x["score"], reverse=True)
        return predictions[:limit]


recommendation_service = RecommendationService()
