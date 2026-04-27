import json
import os
import time

import pandas as pd
from openai import OpenAI


INPUT_CSV = "data/tmdb_movies_with_documents.csv"
OUTPUT_CSV = "data/tmdb_movies_with_embeddings.csv"

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


def load_existing_results(output_csv: str) -> pd.DataFrame:
    if os.path.exists(output_csv):
        return pd.read_csv(output_csv)

    return pd.DataFrame()


def save_results(df: pd.DataFrame, output_csv: str):
    df.to_csv(output_csv, index=False)
    print(f"💾 Saved {len(df)} rows to {output_csv}")


def main():
    source_df = pd.read_csv(INPUT_CSV)
    existing_df = load_existing_results(OUTPUT_CSV)

    completed_ids = set()

    if not existing_df.empty and "embedding" in existing_df.columns:
        completed_ids = set(
            existing_df[
                existing_df["embedding"].notna()
                & (existing_df["embedding"].astype(str).str.strip() != "")
            ]["tmdb_id"].astype(int)
        )

    results = existing_df.to_dict(orient="records") if not existing_df.empty else []

    print(f"Total movies: {len(source_df)}")
    print(f"Already completed: {len(completed_ids)}")

    new_count = 0

    for idx, row in source_df.iterrows():
        tmdb_id = int(row["tmdb_id"])

        if tmdb_id in completed_ids:
            continue

        title = row["title"]
        document = row["document"]

        print(f"[{idx + 1}/{len(source_df)}] Embedding: {title}")

        try:
            embedding = get_embedding(document)
        except Exception as e:
            print(f"[ERROR] Failed embedding for {title}: {e}")
            embedding = None

        row_dict = row.to_dict()
        row_dict["embedding"] = json.dumps(embedding) if embedding is not None else None

        results.append(row_dict)

        if embedding is not None:
            completed_ids.add(tmdb_id)
            new_count += 1

        if new_count > 0 and new_count % 100 == 0:
            save_results(pd.DataFrame(results), OUTPUT_CSV)

        time.sleep(0.1)

    save_results(pd.DataFrame(results), OUTPUT_CSV)
    print(f"✅ Finished. Added {new_count} new embeddings.")


if __name__ == "__main__":
    main()