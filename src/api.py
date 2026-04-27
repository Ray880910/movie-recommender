from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.semantic_search import load_semantic_base, semantic_recommend
from src.preference_update import update_preferences

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
    title_zh: Optional[str] = None
    genres: str
    final_score: Optional[float] = None
    release_year: Optional[int] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None
    director: Optional[str] = None
    top_cast: Optional[str] = None


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
    
    
    updated_preferences = update_preferences(
        message=request.message,
        current_likes=request.likes,
        current_dislikes=request.dislikes,
    )

    updated_likes = updated_preferences["likes"]
    updated_dislikes = updated_preferences["dislikes"]
    shift_type = updated_preferences.get("shift_type", "unknown")
    update_source = updated_preferences.get("update_source", "unknown")
    

    recommendations = semantic_recommend(
        current_message=request.message,
        history=request.history,
        shown_movie_ids=request.shown_movie_ids,
        likes=updated_likes,
        dislikes=updated_dislikes,
        shift_type=shift_type,
        df=semantic_movies_df,
        top_k=5,
        semantic_top_n=300,
        min_vote_count=100,
        semantic_weight=0.7,
        vote_weight=0.1,
        count_weight=0.15,
        popularity_weight=0.05,
    )


    explanation = (
        "系統會根據目前輸入、歷史偏好與排除條件進行語意搜尋，"
        "並排除已推薦過的電影，再結合評分與觀看數進行排序。"
    )

    return {
        "user_message": request.message,
        "parsed_preferences": {
            "reference_titles": [],
            "genres": updated_likes,
            "mood": [shift_type, update_source],
            "exclude": updated_dislikes,
        },
        "seed_movie": None,
        "recommendations": recommendations,
        "explanation": explanation,
    }