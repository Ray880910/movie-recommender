import pandas as pd


def format_genres(genres_text: str) -> str:
    if not isinstance(genres_text, str):
        return ""
    return genres_text.replace("|", ", ")


def build_movie_document(title: str, genres: str, overview: str) -> str:
    genres_text = format_genres(genres)
    overview_text = overview if isinstance(overview, str) else ""

    return (
        f"Title: {title}\n"
        f"Genres: {genres_text}\n"
        f"Overview: {overview_text}"
    )


def process_movies(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)

    df["document"] = df.apply(
        lambda row: build_movie_document(
            title=row["title"],
            genres=row["genres"],
            overview=row["overview"],
        ),
        axis=1,
    )

    df.to_csv(output_csv, index=False)
    print(f"✅ Saved documents to {output_csv}")


if __name__ == "__main__":
    INPUT = "data/movies_with_overview.csv"
    OUTPUT = "data/movies_with_documents.csv"

    process_movies(INPUT, OUTPUT)