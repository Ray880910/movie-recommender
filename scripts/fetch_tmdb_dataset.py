import os
import time
from typing import Dict, List, Optional

import pandas as pd
import requests


TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("請先設定 TMDB_API_KEY 環境變數")


BASE_URL = "https://api.themoviedb.org/3"

OUTPUT_CSV = "data/tmdb_movies.csv"

TODAY = "2026-04-26"
MIN_VOTE_COUNT = 100
MIN_VOTE_AVERAGE = 5.5

MOVIE_LIST_ENDPOINTS = [
    "popular",
    "top_rated",
]

GENRE_MAP: Dict[int, str] = {}


def tmdb_get(path: str, params: Optional[dict] = None) -> dict:
    if params is None:
        params = {}

    params["api_key"] = TMDB_API_KEY
    params.setdefault("language", "en-US")

    url = f"{BASE_URL}{path}"

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    return response.json()


def load_genre_map() -> Dict[int, str]:
    data = tmdb_get("/genre/movie/list")
    genres = data.get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}


def genre_ids_to_names(genre_ids: List[int]) -> str:
    names = []

    for genre_id in genre_ids:
        name = GENRE_MAP.get(genre_id)
        if name:
            names.append(name)

    return "|".join(names)


def extract_director(credits: dict) -> str:
    crew = credits.get("crew", [])

    for person in crew:
        if person.get("job") == "Director":
            return person.get("name") or ""

    return ""


def extract_top_cast(credits: dict, limit: int = 5) -> str:
    cast = credits.get("cast", [])
    names = []

    for person in cast[:limit]:
        name = person.get("name")
        if name:
            names.append(name)

    return "|".join(names)


def fetch_credits(movie_id: int) -> dict:
    try:
        return tmdb_get(f"/movie/{movie_id}/credits")
    except Exception as e:
        print(f"[WARN] Failed credits for {movie_id}: {e}")
        return {}


def fetch_keywords(movie_id: int) -> str:
    try:
        data = tmdb_get(f"/movie/{movie_id}/keywords")
        keywords = data.get("keywords", [])
        names = [item["name"] for item in keywords if item.get("name")]
        return "|".join(names[:10])
    except Exception as e:
        print(f"[WARN] Failed keywords for {movie_id}: {e}")
        return ""


def fetch_movie_list(endpoint: str, page: int) -> List[dict]:
    data = tmdb_get(
        f"/movie/{endpoint}",
        params={"page": page},
    )

    return data.get("results", [])


def normalize_movie(movie: dict) -> dict:
    movie_id = movie.get("id")

    credits = fetch_credits(movie_id)
    keywords = fetch_keywords(movie_id)

    release_date = movie.get("release_date") or ""
    release_year = release_date[:4] if release_date else ""

    return {
        "tmdb_id": movie_id,
        "title": movie.get("title") or movie.get("original_title") or "",
        "release_date": release_date,
        "release_year": release_year,
        "genres": genre_ids_to_names(movie.get("genre_ids", [])),
        "overview": movie.get("overview") or "",
        "director": extract_director(credits),
        "top_cast": extract_top_cast(credits, limit=5),
        "keywords": keywords,
        "vote_average": movie.get("vote_average") or 0,
        "vote_count": movie.get("vote_count") or 0,
        "popularity": movie.get("popularity") or 0,
    }


def is_valid_movie(movie: dict) -> bool:
    overview = movie.get("overview") or ""
    if not overview.strip():
        return False

    if float(movie.get("vote_average", 0)) < MIN_VOTE_AVERAGE:
        return False

    if int(movie.get("vote_count", 0)) < MIN_VOTE_COUNT:
        return False

    release_date = movie.get("release_date")
    if not release_date:
        return False

    release_date = pd.to_datetime(release_date, errors="coerce")
    today = pd.to_datetime(TODAY)

    if pd.isna(release_date):
        return False

    if release_date > today:
        return False

    return True


def load_existing_movies(output_csv: str) -> Dict[int, dict]:
    if not os.path.exists(output_csv):
        return {}

    df = pd.read_csv(output_csv)

    movie_by_id = {}

    for _, row in df.iterrows():
        tmdb_id = row.get("tmdb_id")

        if pd.isna(tmdb_id):
            continue

        movie_by_id[int(tmdb_id)] = row.to_dict()

    print(f"📂 Loaded existing movies: {len(movie_by_id)}")

    return movie_by_id


def save_dataset(movie_by_id: Dict[int, dict], output_csv: str) -> None:
    df = pd.DataFrame(movie_by_id.values())

    if df.empty:
        return

    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)

    df = df.sort_values(
        by=["popularity", "vote_count", "vote_average"],
        ascending=[False, False, False],
    )

    df.to_csv(output_csv, index=False)
    print(f"💾 Auto-saved {len(df)} movies to {output_csv}")


def fetch_tmdb_dataset(
    output_csv: str = OUTPUT_CSV,
    pages_per_endpoint: int = 100,
    sleep_seconds: float = 0.25,
):
    global GENRE_MAP
    GENRE_MAP = load_genre_map()

    movie_by_id = load_existing_movies(output_csv)

    skipped_low_quality = 0
    skipped_duplicate = 0
    added_count = 0

    for endpoint in MOVIE_LIST_ENDPOINTS:
        for page in range(1, pages_per_endpoint + 1):
            print(f"\nFetching endpoint={endpoint}, page={page}")

            try:
                movies = fetch_movie_list(endpoint, page)
            except Exception as e:
                print(f"[WARN] Failed endpoint={endpoint}, page={page}: {e}")
                continue

            for movie in movies:
                movie_id = movie.get("id")

                if not movie_id:
                    continue

                if int(movie_id) in movie_by_id:
                    skipped_duplicate += 1
                    continue

                try:
                    normalized = normalize_movie(movie)

                    if not is_valid_movie(normalized):
                        skipped_low_quality += 1
                        continue

                    movie_by_id[int(movie_id)] = normalized
                    added_count += 1

                    print(
                        f"  Added #{len(movie_by_id)}: "
                        f"{normalized['title']} ({normalized['release_year']}) "
                        f"| popularity={normalized['popularity']} "
                        f"| vote_count={normalized['vote_count']} "
                        f"| vote_average={normalized['vote_average']}"
                    )

                except Exception as e:
                    print(f"[WARN] Failed movie {movie_id}: {e}")

                time.sleep(sleep_seconds)

            save_dataset(movie_by_id, output_csv)

            print(
                f"Progress summary: total={len(movie_by_id)}, "
                f"added={added_count}, "
                f"duplicates={skipped_duplicate}, "
                f"low_quality_or_unreleased={skipped_low_quality}"
            )

    save_dataset(movie_by_id, output_csv)

    print("\n✅ Finished fetching TMDb dataset")
    print(f"Final movies: {len(movie_by_id)}")
    print(f"Added new movies: {added_count}")
    print(f"Skipped duplicates: {skipped_duplicate}")
    print(f"Skipped low quality / unreleased: {skipped_low_quality}")


if __name__ == "__main__":
    fetch_tmdb_dataset(
        output_csv=OUTPUT_CSV,
        pages_per_endpoint=100,
        sleep_seconds=0.25,
    )