import json
import math
import os
from typing import List, Dict

import numpy as np
import pandas as pd
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("請先設定 OPENAI_API_KEY 環境變數")

client = OpenAI(api_key=OPENAI_API_KEY)


EMBEDDINGS_CSV_PATH = "data/movies_with_embeddings.csv"
RATINGS_CSV_PATH = "data/ratings.csv"


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    response = client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def min_max_normalize(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()

    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series([0.0] * len(series), index=series.index)

    return (series - min_val) / (max_val - min_val)


def build_rating_stats(ratings_csv_path: str) -> pd.DataFrame:
    ratings_df = pd.read_csv(ratings_csv_path)

    stats_df = (
        ratings_df.groupby("movieId")
        .agg(
            avg_rating=("rating", "mean"),
            rating_count=("rating", "count"),
        )
        .reset_index()
    )

    return stats_df


def load_semantic_base(
    embeddings_csv_path: str = EMBEDDINGS_CSV_PATH,
    ratings_csv_path: str = RATINGS_CSV_PATH,
) -> pd.DataFrame:
    df = pd.read_csv(embeddings_csv_path)
    stats_df = build_rating_stats(ratings_csv_path)

    df = df.merge(stats_df, on="movieId", how="left")
    df["avg_rating"] = df["avg_rating"].fillna(0.0)
    df["rating_count"] = df["rating_count"].fillna(0.0)

    return df


def semantic_recommend(
    query: str,
    df: pd.DataFrame,
    top_k: int = 5,
    semantic_top_n: int = 300,
    min_rating_count: int = 5,
    semantic_weight: float = 0.7,
    rating_weight: float = 0.1,
    count_weight: float = 0.2,
) -> List[Dict]:
    query_embedding = get_embedding(query)

    semantic_scores = []

    for _, row in df.iterrows():
        embedding_str = row["embedding"]

        if not isinstance(embedding_str, str) or not embedding_str.strip():
            semantic_scores.append(None)
            continue

        movie_embedding = json.loads(embedding_str)
        score = cosine_similarity(query_embedding, movie_embedding)
        semantic_scores.append(score)

    working_df = df.copy()
    working_df["semantic_similarity"] = semantic_scores
    working_df = working_df.dropna(subset=["semantic_similarity"]).copy()

    # Step 1: semantic retrieval
    working_df = (
        working_df.sort_values(by="semantic_similarity", ascending=False)
        .head(semantic_top_n)
        .copy()
    )

    # Step 2: popularity filter
    working_df = working_df[working_df["rating_count"] >= min_rating_count].copy()

    if len(working_df) == 0:
        return []

    # Step 3: rerank
    working_df["log_rating_count"] = working_df["rating_count"].apply(lambda x: math.log1p(x))

    working_df["semantic_norm"] = min_max_normalize(working_df["semantic_similarity"])
    working_df["avg_rating_norm"] = min_max_normalize(working_df["avg_rating"])
    working_df["rating_count_norm"] = min_max_normalize(working_df["log_rating_count"])

    working_df["final_score"] = (
        semantic_weight * working_df["semantic_norm"]
        + rating_weight * working_df["avg_rating_norm"]
        + count_weight * working_df["rating_count_norm"]
    )

    working_df = working_df.sort_values(by="final_score", ascending=False)

    results = []
    for _, row in working_df.head(top_k).iterrows():
        results.append(
            {
                "movieId": int(row["movieId"]),
                "title": row["title"],
                "genres": row["genres"],
                "final_score": float(row["final_score"]),
                "semantic_similarity": float(row["semantic_similarity"]),
                "avg_rating": float(row["avg_rating"]),
                "rating_count": int(row["rating_count"]),
            }
        )

    return results