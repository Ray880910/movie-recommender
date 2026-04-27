import numpy as np
import pandas as pd


CSV_PATH = "data/tmdb_movies.csv"

df = pd.read_csv(CSV_PATH)

print(f"\nTotal movies: {len(df)}")


# -------------------------
# Year cleanup / distribution
# -------------------------

# 安全轉 numeric，避免 2024.0 被 isnumeric() 擋掉
df["release_year"] = pd.to_numeric(
    df["release_year"],
    errors="coerce"
)

# 移除沒有年份的
df = df.dropna(subset=["release_year"]).copy()

df["release_year"] = df["release_year"].astype(int)

print("\nMovies per year (recent 20 years):")
print(
    df[df["release_year"] >= 2005]
    .groupby("release_year")
    .size()
)


# -------------------------
# vote_average distribution
# -------------------------

print("\nVote average stats:")
print(
    df["vote_average"].describe()
)


# -------------------------
# vote_count distribution
# -------------------------

print("\nVote count stats:")
print(
    df["vote_count"].describe()
)


print("\nLog vote_count stats:")
print(
    pd.Series(
        np.log1p(df["vote_count"])
    ).describe()
)


# -------------------------
# old movies ratio
# -------------------------

old_count = df[df["release_year"] < 1980].shape[0]

print("\nMovies before 1980:")
print(old_count)

print("\nRatio:")

if len(df) > 0:
    print(old_count / len(df))
else:
    print("No valid year data.")


# -------------------------
# top popularity
# -------------------------

print("\nTop 50 by popularity:")

print(
    df.sort_values(
        by=["popularity"],
        ascending=False
    )[
        [
            "title",
            "release_year",
            "popularity",
            "vote_count",
            "vote_average",
        ]
    ].head(50)
)


# -------------------------
# extra sanity checks
# -------------------------

print("\nMissing overview count:")
print(
    df["overview"].isna().sum()
)

print("\nMissing director count:")
print(
    df["director"].isna().sum()
)

print("\nTop genres:")
print(
    df["genres"]
    .str.split("|")
    .explode()
    .value_counts()
    .head(20)
)


# -------------------------
# top50 average_score, vote_count, hybrid_score(average score & vote_count)
# -------------------------



print("\nTop 50 by vote_average:")
print(
    df.sort_values(
        by=["vote_average", "vote_count"],
        ascending=[False, False]
    )[
        [
            "title",
            "release_year",
            "vote_average",
            "vote_count",
            "popularity",
        ]
    ].head(50)
)


print("\nTop 50 by vote_count:")
print(
    df.sort_values(
        by=["vote_count", "vote_average"],
        ascending=[False, False]
    )[
        [
            "title",
            "release_year",
            "vote_average",
            "vote_count",
            "popularity",
        ]
    ].head(50)
)


df["quality_score"] = (
    df["vote_average"] * np.log1p(df["vote_count"])
)

print("\nTop 50 by quality_score:")
print(
    df.sort_values(
        by=["quality_score"],
        ascending=False
    )[
        [
            "title",
            "release_year",
            "vote_average",
            "vote_count",
            "popularity",
            "quality_score",
        ]
    ].head(50)
)