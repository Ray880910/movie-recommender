import numpy as np
import pandas as pd


INPUT_CSV = "data/tmdb_movies.csv"
OUTPUT_CSV = "data/tmdb_movies.csv"

TODAY = "2026-04-26"

MIN_VOTE_COUNT = 100
MIN_VOTE_AVERAGE = 5.5

DECADE_LIMITS = {
    "2020s": 800,
    "2010s": 700,
    "2000s": 600,
    "1990s": 400,
    "1980s": 250,
    "before_1980": 150,
}


def get_decade_group(year: int) -> str:
    if year >= 2020:
        return "2020s"
    if year >= 2010:
        return "2010s"
    if year >= 2000:
        return "2000s"
    if year >= 1990:
        return "1990s"
    if year >= 1980:
        return "1980s"
    return "before_1980"


df = pd.read_csv(INPUT_CSV)

print(f"Original movies: {len(df)}")

# release_date cleanup
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
today = pd.to_datetime(TODAY)

# release_year cleanup
df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")

# numeric cleanup
df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)

# 基本品質過濾
filtered = df[
    (df["release_date"].notna()) &
    (df["release_date"] <= today) &
    (df["overview"].notna()) &
    (df["overview"].astype(str).str.strip() != "") &
    (df["vote_count"] >= MIN_VOTE_COUNT) &
    (df["vote_average"] >= MIN_VOTE_AVERAGE)
].copy()

filtered["release_year"] = filtered["release_year"].astype(int)

print(f"After quality filter: {len(filtered)}")

# quality score：避免只有高分但票數少的電影衝太前
filtered["quality_score"] = (
    filtered["vote_average"] * np.log1p(filtered["vote_count"])
    + 0.05 * filtered["popularity"]
)

filtered["decade_group"] = filtered["release_year"].apply(get_decade_group)

# 年代平衡：每個年代依 quality_score 取前 N 部
balanced_parts = []

for decade, limit in DECADE_LIMITS.items():
    part = filtered[filtered["decade_group"] == decade].copy()
    part = part.sort_values(
        by=["quality_score", "vote_count", "vote_average"],
        ascending=[False, False, False],
    ).head(limit)

    balanced_parts.append(part)

    print(f"{decade}: kept {len(part)} movies")

cleaned = pd.concat(balanced_parts, ignore_index=True)

cleaned = cleaned.sort_values(
    by=["quality_score", "vote_count", "vote_average"],
    ascending=[False, False, False],
)

# 輸出前刪掉輔助欄位也可以；我先保留 quality_score 和 decade_group 方便檢查
cleaned.to_csv(OUTPUT_CSV, index=False)

print(f"\nSaved cleaned dataset: {OUTPUT_CSV}")
print(f"Final movies: {len(cleaned)}")

print("\nMovies per decade:")
print(cleaned["decade_group"].value_counts())

print("\nMovies per year after cleaning:")
print(cleaned.groupby("release_year").size().tail(30))

print("\nTop 20 by quality_score:")
print(
    cleaned[
        [
            "title",
            "release_year",
            "vote_average",
            "vote_count",
            "popularity",
            "quality_score",
            "decade_group",
        ]
    ].head(20)
)