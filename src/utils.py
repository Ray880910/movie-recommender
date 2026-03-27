import pandas as pd


def find_movie_by_title(movies: pd.DataFrame, keyword: str):
    keyword = keyword.lower()
    result = movies[movies["title"].str.lower().str.contains(keyword, na=False)].copy()
    return result[["movieId", "title", "genres"]]


def get_movie_by_id(movies: pd.DataFrame, movie_id: int):
    result = movies[movies["movieId"] == movie_id].copy()
    return result[["movieId", "title", "genres"]]