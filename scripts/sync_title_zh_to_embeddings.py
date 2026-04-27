import pandas as pd

SOURCE_CSV = "data/tmdb_movies.csv"
TARGET_CSV = "data/tmdb_movies_with_embeddings.csv"

source_df = pd.read_csv(SOURCE_CSV)
target_df = pd.read_csv(TARGET_CSV)

source_titles = source_df[["tmdb_id", "title_zh"]].copy()

target_df = target_df.drop(columns=["title_zh"], errors="ignore")
target_df = target_df.merge(source_titles, on="tmdb_id", how="left")

target_df["title_zh"] = target_df["title_zh"].fillna(target_df["title"])

target_df.to_csv(TARGET_CSV, index=False)

print(f"Synced title_zh to {TARGET_CSV}")
print(target_df[["title", "title_zh"]].head(20))