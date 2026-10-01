import requests
from urllib.parse import quote
from backend.config import settings


def fetch_omdb_metadata(title: str):
    try:
        clean_title = title.split("(")[0].strip() if "(" in title else title
        res = requests.get(
            f"http://www.omdbapi.com/?apikey={settings.OMDB_API_KEY}&t={quote(clean_title)}",
            timeout=5,
        )
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None
