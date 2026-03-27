from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_movies():
    return pd.read_csv(DATA_DIR / "movies.csv")


def load_ratings():
    return pd.read_csv(DATA_DIR / "ratings.csv")


def load_data():
    movies = load_movies()
    ratings = load_ratings()
    return movies, ratings
