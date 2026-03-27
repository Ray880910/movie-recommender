import pandas as pd


def get_user_liked_movies(ratings: pd.DataFrame, user_id: int, threshold: float = 4.0):
    user_ratings = ratings[ratings["userId"] == user_id]
    liked_movies = user_ratings[user_ratings["rating"] >= threshold]["movieId"].tolist()
    return liked_movies


def precision_at_k(recommended_movie_ids, relevant_movie_ids, k: int):
    recommended_top_k = recommended_movie_ids[:k]
    hits = sum(1 for movie_id in recommended_top_k if movie_id in relevant_movie_ids)
    return hits / k if k > 0 else 0.0


def evaluate_single_user_item_based(
    user_id: int,
    liked_movie_id: int,
    ratings: pd.DataFrame,
    recommend_func,
    k: int = 10,
    threshold: float = 4.0,
):
    liked_movies = get_user_liked_movies(ratings, user_id, threshold=threshold)

    # 不把輸入那部片本身算進 relevant
    relevant_movie_ids = [m for m in liked_movies if m != liked_movie_id]

    recommendations = recommend_func(liked_movie_id)
    if recommendations.empty:
        return 0.0

    recommended_movie_ids = recommendations["movieId"].tolist()
    return precision_at_k(recommended_movie_ids, relevant_movie_ids, k)