import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def build_user_item_matrix(ratings: pd.DataFrame):
    # user x movie matrix
    return ratings.pivot_table(index="userId", columns="movieId", values="rating")


def build_item_similarity_matrix(user_item_matrix: pd.DataFrame):
    # 根據user對movie的評分方式計算movie的similarity
    item_user_matrix = user_item_matrix.T.fillna(0)

    similarity = cosine_similarity(item_user_matrix)

    similarity_df = pd.DataFrame(
        similarity,
        index=item_user_matrix.index,
        columns=item_user_matrix.index,
    )

    return similarity_df


def recommend_similar_movies(movie_id, similarity_df, movies, top_n=10):
    if movie_id not in similarity_df.index:
        return pd.DataFrame()

    similar_scores = similarity_df[movie_id].sort_values(ascending=False)

    # 移除自己
    similar_scores = similar_scores.drop(movie_id, errors="ignore")

    # 取前 N 個
    similar_scores = similar_scores.head(top_n)

    result = movies[movies["movieId"].isin(similar_scores.index)].copy()
    result["similarity_score"] = result["movieId"].map(similar_scores)

    return result.sort_values(by="similarity_score", ascending=False)