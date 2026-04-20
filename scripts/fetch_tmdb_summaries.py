import os
import re
import time
import requests
import pandas as pd

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("請先設定 TMDB_API_KEY 環境變數")

# ---------------------------------------
# 工具：拆 title 和 year

def split_title_and_year(raw_title: str):
    match = re.match(r"^(.*)\s\((\d{4})\)$", raw_title)
    if match:
        return match.group(1).strip(), match.group(2)
    return raw_title.strip(), None


# ---------------------------------------
# Step 1：搜尋電影（拿 TMDb ID）

def search_movie(title: str, year: str | None = None):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US",
    }
    if year:
        params["year"] = year

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        print(f"[ERROR] search_movie failed: {title}, {e}")
        return []


# ---------------------------------------
# Step 2：取得詳細資料（overview）

def get_movie_details(tmdb_id: int):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[ERROR] get_movie_details failed: {tmdb_id}, {e}")
        return {}


# ---------------------------------------
# Step 3：從 title 拿 summary

def fetch_overview(raw_title: str):
    title, year = split_title_and_year(raw_title)

    results = search_movie(title, year)
    if not results:
        return None, None

    # 取第一筆（簡單策略）
    best = results[0]
    tmdb_id = best.get("id")

    if not tmdb_id:
        return None, None

    details = get_movie_details(tmdb_id)
    overview = details.get("overview")

    return tmdb_id, overview


# ---------------------------------------
# Step 4：批次處理 movies.csv

def process_movies(input_csv: str, output_csv: str, limit: int | None = None):
    df = pd.read_csv(input_csv)

    results = []

    for idx, row in df.iterrows():
        if limit and idx >= limit:
            break

        movie_id = row["movieId"]
        title = row["title"]
        genres = row["genres"]

        print(f"[{idx}] Processing: {title}")

        tmdb_id, overview = fetch_overview(title)

        results.append({
            "movieId": movie_id,
            "title": title,
            "genres": genres,
            "tmdb_id": tmdb_id,
            "overview": overview
        })

        # 避免打爆 API（很重要🔥）
        time.sleep(0.2)

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_csv, index=False)

    print(f"✅ Saved to {output_csv}")


# ---------------------------------------
# main

if __name__ == "__main__":
    INPUT = "data/movies.csv"
    OUTPUT = "data/movies_with_overview.csv"

    process_movies(INPUT, OUTPUT, limit=None)