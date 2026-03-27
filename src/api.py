import os
import json
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

from src.load_data import load_data
from src.collaborative import (
    build_user_item_matrix,
    build_item_similarity_matrix,
)
from src.content_based import build_content_similarity_matrix
from src.hybrid import recommend_hybrid
from src.utils import find_movie_by_title, get_movie_by_id


#==============================================
# Pydantic Model

class Movie(BaseModel):
    movieId: int
    title: str
    genres: str


class Recommendation(BaseModel):
    movieId: int
    title: str
    genres: str
    final_score: float


class RecommendationResponse(BaseModel):
    input_movie: Movie
    recommendations: List[Recommendation]


class ChatRecommendRequest(BaseModel):
    message: str


class ParsedPreferences(BaseModel):
    reference_titles: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    mood: List[str] = Field(default_factory=list)
    exclude: List[str] = Field(default_factory=list)


class ChatRecommendation(BaseModel):
    movieId: int
    title: str
    genres: str
    final_score: Optional[float] = None


class ChatRecommendResponse(BaseModel):
    user_message: str
    parsed_preferences: ParsedPreferences
    seed_movie: Optional[Movie] = None
    recommendations: List[ChatRecommendation]
    explanation: str

#==============================================
# App Setup  

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#==============================================
# Preload Data

movies, ratings = load_data()

user_item_matrix = build_user_item_matrix(ratings)
collaborative_similarity_df = build_item_similarity_matrix(user_item_matrix)
content_similarity_df = build_content_similarity_matrix(movies)


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


#==============================================
# Helper Functions

def parse_preferences_with_llm(user_message: str) -> ParsedPreferences:
    prompt = f"""
你是一個電影推薦系統的偏好解析器。

請根據使用者輸入，抽取以下欄位，並「合理推測」缺失資訊：

- reference_titles: 使用者提到的電影名稱列表
- genres: 根據描述或電影推測類型（例如 Sci-Fi, Drama）
- mood: 推測風格（例如 mind-bending, emotional, fast-paced）
- exclude: 不想要的條件

規則：
- 如果使用者提到電影（例如 Inception），請根據該電影補出 genres 與 mood
- 不要留空，能推就推
- 只輸出 JSON，不要多餘文字

輸出格式：
{{
  "reference_titles": ["Toy Story"],
  "genres": ["Animation", "Children"],
  "mood": ["heartwarming"],
  "exclude": []
}}

使用者輸入：
{user_message}
""".strip()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    text = response.output_text.strip()
    print("LLM raw output:", text)

    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM 回傳格式錯誤")

    # 明確整理欄位，避免 None 或非 list
    cleaned = {
        "reference_titles": parsed_json.get("reference_titles") or [],
        "genres": parsed_json.get("genres") or [],
        "mood": parsed_json.get("mood") or [],
        "exclude": parsed_json.get("exclude") or [],
    }

    parsed = ParsedPreferences(**cleaned)
    print("Parsed model_dump:", parsed.model_dump())

    return parsed


def get_seed_movie_id_from_preferences(parsed: ParsedPreferences) -> int:
    # 如果 LLM 有抓到電影名稱
    if parsed.reference_titles:
        title = parsed.reference_titles[0]

        matched = find_movie_by_title(movies, title)

        if not matched.empty:
            return int(matched.iloc[0]["movieId"])

    # fallback（找不到就用預設）
    return 1


def recommend_by_genres(parsed: ParsedPreferences, top_n: int = 5):
    if not parsed.genres:
        return []

    genre_keywords = [g.lower() for g in parsed.genres]

    matched_movies = movies.copy()

    def count_matching_genres(genres_text: str) -> int:
        if not isinstance(genres_text, str):
            return 0

        movie_genres = [g.strip().lower() for g in genres_text.split("|")]
        return sum(1 for keyword in genre_keywords if keyword in movie_genres)

    matched_movies["match_count"] = matched_movies["genres"].apply(count_matching_genres)
    matched_movies = matched_movies[matched_movies["match_count"] > 0].copy()

    if matched_movies.empty:
        return []

    rating_stats = (
        ratings.groupby("movieId")
        .agg(
            avg_rating=("rating", "mean"),
            rating_count=("rating", "count"),
        )
        .reset_index()
    )

    matched_movies = matched_movies.merge(rating_stats, on="movieId", how="left")
    matched_movies["avg_rating"] = matched_movies["avg_rating"].fillna(0)
    matched_movies["rating_count"] = matched_movies["rating_count"].fillna(0)

    matched_movies = matched_movies.sort_values(
        by=["match_count", "rating_count", "avg_rating", "title"],
        ascending=[False, False, False, True]
    ).head(top_n)

    results = []
    for _, row in matched_movies.iterrows():
        results.append(
            {
                "movieId": int(row["movieId"]),
                "title": row["title"],
                "genres": row["genres"],
                "final_score": float(row["match_count"]),
            }
        )

    return results


def build_explanation(
    parsed: ParsedPreferences,
    seed_movie: dict | None,
    route_type: str,
) -> str:
    genres_text = "、".join(parsed.genres) if parsed.genres else "未指定類型"
    mood_text = "、".join(parsed.mood) if parsed.mood else "未指定風格"

    if route_type == "reference" and seed_movie:
        return (
            f"系統偵測到你提到的參考電影是《{seed_movie['title']}》，"
            f"並結合你偏好的類型（{genres_text}）與風格（{mood_text}），"
            "推薦出觀眾喜好與內容特徵相近的電影。"
        )

    if route_type == "genre":
        return (
            f"系統沒有找到明確的參考電影，因此根據你描述的類型偏好（{genres_text}）"
            f"與風格（{mood_text}）進行推薦。"
        )

    return (
        "系統沒有解析到足夠明確的偏好，因此暫時使用預設推薦邏輯提供結果。"
    )

#==============================================
# Route

@app.get("/")
def root():
    return {"message": "Movie Recommender API is running"}


@app.get("/movies/search")
def search_movies(keyword: str = Query(..., min_length=1)):
    matched_movies = find_movie_by_title(movies, keyword)

    return {
        "keyword": keyword,
        "count": len(matched_movies),
        "results": matched_movies.to_dict(orient="records"),
    }


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie_info = get_movie_by_id(movies, movie_id)

    if movie_info.empty:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie_info.to_dict(orient="records")[0]


@app.get("/recommend", response_model=RecommendationResponse)
def recommend(movie_id: int, top_n: int = 10, alpha: float = 0.7):
    movie_info = get_movie_by_id(movies, movie_id)

    if movie_info.empty:
        raise HTTPException(status_code=404, detail="Movie not found")

    recommendations = recommend_hybrid(
        movie_id=movie_id,
        collaborative_similarity_df=collaborative_similarity_df,
        content_similarity_df=content_similarity_df,
        movies=movies,
        top_n=top_n,
        alpha=alpha,
    )

    return {
        "input_movie": movie_info.to_dict(orient="records")[0],
        "recommendations": recommendations.to_dict(orient="records"),
    }


@app.post("/chat-recommend", response_model=ChatRecommendResponse)
def chat_recommend(request: ChatRecommendRequest):
    parsed = parse_preferences_with_llm(request.message)

    print("Parsed model_dump:", parsed.model_dump())

    seed_movie = None
    recommendations = []
    route_type = "fallback"

    # 情況 1：有 reference movie
    if parsed.reference_titles:
        route_type = "reference"

        seed_movie_id = get_seed_movie_id_from_preferences(parsed)
        print("Seed movie id:", seed_movie_id)

        seed_movie_info = get_movie_by_id(movies, seed_movie_id)
        if not seed_movie_info.empty:
            seed_movie = seed_movie_info.to_dict(orient="records")[0]

        recommendations_df = recommend_hybrid(
            movie_id=seed_movie_id,
            collaborative_similarity_df=collaborative_similarity_df,
            content_similarity_df=content_similarity_df,
            movies=movies,
            top_n=5,
            alpha=0.7,
        )

        recommendations = recommendations_df.to_dict(orient="records")

    # 情況 2：沒有 reference movie，但有 genres
    elif parsed.genres:
        route_type = "genre"
        recommendations = recommend_by_genres(parsed, top_n=5)

    # 情況 3：fallback
    else:
        seed_movie_id = 1
        seed_movie_info = get_movie_by_id(movies, seed_movie_id)
        if not seed_movie_info.empty:
            seed_movie = seed_movie_info.to_dict(orient="records")[0]

        recommendations_df = recommend_hybrid(
            movie_id=seed_movie_id,
            collaborative_similarity_df=collaborative_similarity_df,
            content_similarity_df=content_similarity_df,
            movies=movies,
            top_n=5,
            alpha=0.7,
        )

        recommendations = recommendations_df.to_dict(orient="records")

    explanation = build_explanation(
        parsed=parsed,
        seed_movie=seed_movie,
        route_type=route_type,
    )

    return {
        "user_message": request.message,
        "parsed_preferences": parsed.model_dump(),
        "seed_movie": seed_movie,
        "recommendations": recommendations,
        "explanation": explanation,
    }