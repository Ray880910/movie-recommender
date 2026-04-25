from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.semantic_search import load_semantic_base, semantic_recommend


# ==============================================
# Pydantic Models
# ==============================================

class ChatRecommendRequest(BaseModel):
    message: str
    history: List[str] = Field(default_factory=list)
    shown_movie_ids: List[int] = Field(default_factory=list)
    likes: List[str] = Field(default_factory=list)
    dislikes: List[str] = Field(default_factory=list)


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
    seed_movie: Optional[dict] = None
    recommendations: List[ChatRecommendation]
    explanation: str


# ==============================================
# App Setup
# ==============================================

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


# ==============================================
# Preload Data
# ==============================================

semantic_movies_df = load_semantic_base()


# ==============================================
# Routes
# ==============================================

@app.get("/")
def root():
    return {"message": "Semantic Movie Recommender API is running"}


@app.post("/chat-recommend", response_model=ChatRecommendResponse)
def chat_recommend(request: ChatRecommendRequest):
    recommendations = semantic_recommend(
        current_message=request.message,
        history=request.history,
        shown_movie_ids=request.shown_movie_ids,
        likes=request.likes,
        dislikes=request.dislikes,
        df=semantic_movies_df,
        top_k=5,
        semantic_top_n=300,
        min_rating_count=5,
        semantic_weight=0.7,
        rating_weight=0.1,
        count_weight=0.2,
    )

    explanation = (
        "系統會根據目前輸入、歷史偏好與排除條件進行語意搜尋，"
        "並排除已推薦過的電影，再結合評分與觀看數進行排序。"
    )

    return {
        "user_message": request.message,
        "parsed_preferences": {
            "reference_titles": [],
            "genres": request.likes,
            "mood": [],
            "exclude": request.dislikes,
        },
        "seed_movie": None,
        "recommendations": recommendations,
        "explanation": explanation,
    }