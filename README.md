Features:

🎬 Semantic Recommendation (Core)

Users can input natural language:
	•	“I want a warm animated movie about friendship”
	•	“Recommend emotional drama movies”
	•	“Suggest mind-bending sci-fi films”

The system will:
	1.	Convert user input into embeddings
	2.	Perform semantic search against movie descriptions
	3.	Apply a two-stage recommendation pipeline:
		•	Semantic Retrieval
		•	Find top-N most similar movies using cosine similarity
		•	Reranking (Popularity-aware)
			•	Semantic similarity
			•	Average rating
			•	Rating count (popularity)

⸻

Tech Stack

Backend
	•	FastAPI
	•	Python
	•	OpenAI API (Embeddings)
	•	Pandas/NumPy

Recommendation System
	•	Semantic Search (Embedding-based)
	•	Cosine Similarity
	•	Two-stage pipeline:
		•	Retrieval
		•	Reranking
	•	Popularity-aware ranking:
		•	avg_rating
		•	rating_count (log-scaled)

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