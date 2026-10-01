import pickle
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from backend.models.movie import Movie


class RecommendationService:
    def __init__(self):
        self.models = {}
        self._load_models()

    def _load_models(self):
        for algo in ["svd", "knn", "baseline"]:
            try:
                with open(f"backend/models_ml/{algo}_model.pkl", "rb") as f:
                    self.models[algo] = pickle.load(f)
            except Exception:
                try:
                    with open(f"backend/models/{algo}_model.pkl", "rb") as f:
                        self.models[algo] = pickle.load(f)
                except Exception:
                    self.models[algo] = None

    def get_recommendations(
        self, user_id: int, algo: str, db: Session, limit: int = 12
    ):
        model = self.models.get(algo)
        if not model:
            raise ValueError(f"Model {algo} not trained or unavailable.")

        sample_movies = db.query(Movie).order_by(func.random()).limit(300).all()
        predictions = []
        for m in sample_movies:
            pred = model.predict(uid=user_id, iid=m.movie_id)
            predictions.append(
                {
                    "movieId": m.movie_id,
                    "title": m.title,
                    "genres": m.genres,
                    "poster_url": m.poster_url,
                    "score": pred.est,
                    "reason": f"Matches your taste profile ({algo.upper()})",
                }
            )

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
        model = self.models.get(algo)
        if not model:
            raise ValueError(f"Model {algo} not trained.")

        # Sample modern movies with posters for best visual experience
        sample_movies = (
            db.query(Movie)
            .filter(Movie.poster_url != None)
            .order_by(func.random())
            .limit(400)
            .all()
        )
        predictions = []
        for m in sample_movies:
            pred1 = model.predict(uid=user1_id, iid=m.movie_id)
            pred2 = model.predict(uid=user2_id, iid=m.movie_id)

            # Harmonic mean to ensure BOTH users like it (penalizes if one hates it)
            combined_score = (
                (2 * pred1.est * pred2.est) / (pred1.est + pred2.est)
                if (pred1.est + pred2.est) > 0
                else 0
            )

            predictions.append(
                {
                    "movieId": m.movie_id,
                    "title": m.title,
                    "genres": m.genres,
                    "poster_url": m.poster_url,
                    "score": round(combined_score, 2),
                    "user1_score": round(pred1.est, 2),
                    "user2_score": round(pred2.est, 2),
                    "reason": f"99% Match for both of you!",
                }
            )

        predictions.sort(key=lambda x: x["score"], reverse=True)
        return predictions[:limit]


recommendation_service = RecommendationService()
