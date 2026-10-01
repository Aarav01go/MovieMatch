import os
import requests

POSTER_DIR = "static/posters"
os.makedirs(POSTER_DIR, exist_ok=True)


def download_and_cache_poster(url: str, movie_id: int):
    if not url or url == "N/A":
        return None
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            ext = url.split(".")[-1]
            if len(ext) > 4:
                ext = "jpg"
            filename = f"{movie_id}.{ext}"
            filepath = os.path.join(POSTER_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(res.content)
            return f"/static/posters/{filename}"
    except Exception as e:
        print(f"Error caching poster: {e}")
    return None
