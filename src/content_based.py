import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_content_similarity_matrix(movies: pd.DataFrame):
    movies = movies.copy()
    movies["genres"] = movies["genres"].fillna("")

    vectorizer = CountVectorizer(
        tokenizer=lambda x: x.split("|"),
        token_pattern=None
    )

    genre_matrix = vectorizer.fit_transform(movies["genres"])

    similarity = cosine_similarity(genre_matrix)

    similarity_df = pd.DataFrame(
        similarity,
        index=movies["movieId"],
        columns=movies["movieId"],
    )

    return similarity_df


def recommend_by_content(movie_id: int, similarity_df: pd.DataFrame, movies: pd.DataFrame, top_n: int = 10):
    if movie_id not in similarity_df.index:
        return pd.DataFrame()

    similar_scores = similarity_df[movie_id].sort_values(ascending=False)
    similar_scores = similar_scores.drop(movie_id, errors="ignore").head(top_n)

    result = movies[movies["movieId"].isin(similar_scores.index)].copy()
    result["similarity_score"] = result["movieId"].map(similar_scores)
    result = result.sort_values(by="similarity_score", ascending=False)

    return result[["movieId", "title", "genres", "similarity_score"]]