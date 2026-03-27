from src.load_data import load_data
from src.collaborative import (
    build_user_item_matrix,
    build_item_similarity_matrix,
)
from src.content_based import (
    build_content_similarity_matrix,
)
from src.hybrid import recommend_hybrid
from src.utils import find_movie_by_title, get_movie_by_id


def build_all_similarity(movies, ratings):
    user_item_matrix = build_user_item_matrix(ratings)
    collaborative_similarity_df = build_item_similarity_matrix(user_item_matrix)
    content_similarity_df = build_content_similarity_matrix(movies)
    return collaborative_similarity_df, content_similarity_df


if __name__ == "__main__":
    movies, ratings = load_data()

    collaborative_similarity_df, content_similarity_df = build_all_similarity(movies, ratings)

    print("=== Movie Recommender ===")
    print("1. Search movie by title")
    print("2. Recommend by movieId")

    choice = input("Choose an option (1 or 2): ").strip()

    if choice == "1":
        keyword = input("Enter movie title keyword: ").strip()
        matched_movies = find_movie_by_title(movies, keyword)

        if matched_movies.empty:
            print("No movies found.")
        else:
            print("\nMatched movies:")
            print(matched_movies.head(20).to_string(index=False))

    elif choice == "2":
        movie_id_input = input("Enter movieId: ").strip()

        if not movie_id_input.isdigit():
            print("Invalid movieId. Please enter a number.")
        else:
            movie_id = int(movie_id_input)

            movie_info = get_movie_by_id(movies, movie_id)

            if movie_info.empty:
                print("Movie not found.")
            else:
                print("\nSelected movie:")
                print(movie_info.to_string(index=False))

                recommendations = recommend_hybrid(
                    movie_id=movie_id,
                    collaborative_similarity_df=collaborative_similarity_df,
                    content_similarity_df=content_similarity_df,
                    movies=movies,
                    top_n=10,
                    alpha=0.7,
                )

                print("\nTop 10 recommendations:")
                print(
                    recommendations[
                        ["movieId", "title", "genres", "final_score"]
                    ].to_string(index=False)
                )

    else:
        print("Invalid option.")