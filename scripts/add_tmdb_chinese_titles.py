import os
import time

import pandas as pd
import requests


TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("請先設定 TMDB_API_KEY 環境變數")


BASE_URL = "https://api.themoviedb.org/3"

INPUT_CSV = "data/tmdb_movies.csv"
OUTPUT_CSV = "data/tmdb_movies.csv"


def fetch_chinese_title(tmdb_id: int) -> str:
    url = f"{BASE_URL}/movie/{tmdb_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "zh-TW",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    return data.get("title") or ""


def main():
    df = pd.read_csv(INPUT_CSV)

    if "title_zh" not in df.columns:
        df["title_zh"] = ""

    total = len(df)

    for idx, row in df.iterrows():
        tmdb_id = int(row["tmdb_id"])
        title = row.get("title", "")
        existing_title_zh = row.get("title_zh", "")

        if isinstance(existing_title_zh, str) and existing_title_zh.strip():
            continue

        try:
            title_zh = fetch_chinese_title(tmdb_id)

            # 如果 TMDb 沒有繁中片名，fallback 成英文 title
            if not title_zh.strip():
                title_zh = title

            df.at[idx, "title_zh"] = title_zh

            print(
                f"[{idx + 1}/{total}] "
                f"{title} -> {title_zh}"
            )

        except Exception as e:
            print(f"[WARN] Failed title_zh for {title} ({tmdb_id}): {e}")
            df.at[idx, "title_zh"] = title

        if (idx + 1) % 100 == 0:
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"💾 Auto-saved {idx + 1}/{total}")

        time.sleep(0.15)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Finished. Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()