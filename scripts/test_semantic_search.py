from src.semantic_search import load_semantic_base, semantic_recommend

if __name__ == "__main__":
    df = load_semantic_base()

    query = "I want a warm animated movie about friendship and family"

    results = semantic_recommend(
        query=query,
        df=df,
        top_k=5,
        semantic_top_n=300,
        min_rating_count=5,
        semantic_weight=0.7,
        rating_weight=0.1,
        count_weight=0.2,
    )

    print(f"Query: {query}\n")

    for rank, movie in enumerate(results, start=1):
        print(f"{rank}. {movie['title']}")
        print(f"   Genres: {movie['genres']}")
        print(f"   Semantic: {movie['semantic_similarity']:.4f}")
        print(f"   Rating: {movie['avg_rating']:.2f}")
        print(f"   Count: {movie['rating_count']}")
        print(f"   Final: {movie['final_score']:.4f}")
        print()