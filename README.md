Features:

Traditional Recommendation
	•	Search movies by title
	•	Click a movie to get recommendations
	•	Hybrid recommendation system:
	•	Collaborative Filtering
	•	Content-Based Filtering

⸻

AI-powered Recommendation (LLM)

Users can input natural language:
	•	“I want movies like Inception”
	•	“Recommend warm animated movies”
	•	“Suggest mind-bending sci-fi films”

The system will:
	1.	Use LLM to extract:
	•	Reference movies
	•	Genres
	•	Mood
	2.	Automatically choose recommendation strategy:
	•	Reference-based → Hybrid recommendation
	•	Genre-based → Fallback recommendation
	•	Default → General recommendation

⸻

Tech Stack

Backend
	•	FastAPI
	•	Python
	•	OpenAI API (LLM)
	•	Pandas

Recommendation System
	•	Collaborative Filtering
	•	Content-Based Filtering
	•	Hybrid Recommendation
	•	Popularity-aware ranking (rating_count + avg_rating)

Frontend
	•	React (Vite)
	•	Fetch API

DevOps
	•	Docker
	•	Docker Compose

⸻

Installation (Local Development)

Backend
    pip install -r requirements.txt
    export OPENAI_API_KEY=your_api_key
    uvicorn src.api:app --reload

Frontend
    cd frontend
    npm install
    npm run dev

⸻

Run with Docker

touch .env
OPENAI_API_KEY=your_api_key(in .env)
docker compose up --build