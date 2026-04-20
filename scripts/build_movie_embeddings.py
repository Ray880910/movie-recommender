import json
import os
import time

import pandas as pd
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("請先設定 OPENAI_API_KEY 環境變數")

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    response = client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding


def save_results(results: list[dict], output_csv: str) -> None:
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_csv, index=False)
    print(f"💾 Auto-saved {len(results)} rows to {output_csv}")


def load_existing_results(output_csv: str) -> list[dict]:
    if not os.path.exists(output_csv):
        return []

    df_existing = pd.read_csv(output_csv)
    if df_existing.empty:
        return []

    print(f"📂 Loaded existing output: {len(df_existing)} rows")
    return df_existing.to_dict(orient="records")


def process_movies(
    input_csv: str,
    output_csv: str,
    autosave_every: int = 100,
):
    df = pd.read_csv(input_csv)

    existing_results = load_existing_results(output_csv)
    completed_ids = {
        row["movieId"]
        for row in existing_results
        if pd.notna(row.get("embedding")) and str(row.get("embedding")).strip()
    }

    results = existing_results.copy()

    total = len(df)
    processed_since_save = 0
    new_count = 0

    for idx, row in df.iterrows():
        movie_id = row["movieId"]

        if movie_id in completed_ids:
            continue

        title = row["title"]
        genres = row["genres"]
        tmdb_id = row["tmdb_id"]
        overview = row["overview"]
        document = row["document"]

        print(f"[{idx + 1}/{total}] Embedding: {title}")

        try:
            embedding = get_embedding(document)
        except Exception as e:
            print(f"[ERROR] Failed embedding for {title}: {e}")
            embedding = None

        results.append(
            {
                "movieId": movie_id,
                "title": title,
                "genres": genres,
                "tmdb_id": tmdb_id,
                "overview": overview,
                "document": document,
                "embedding": json.dumps(embedding) if embedding is not None else None,
            }
        )

        if embedding is not None:
            completed_ids.add(movie_id)

        processed_since_save += 1
        new_count += 1

        if processed_since_save >= autosave_every:
            save_results(results, output_csv)
            processed_since_save = 0

        time.sleep(0.1)

    # 最後不足 autosave_every 的也存一次
    save_results(results, output_csv)
    print(f"✅ Finished. Added {new_count} new embeddings.")


if __name__ == "__main__":
    INPUT = "data/movies_with_documents.csv"
    OUTPUT = "data/movies_with_embeddings.csv"

    process_movies(
        input_csv=INPUT,
        output_csv=OUTPUT,
        autosave_every=100,
    )