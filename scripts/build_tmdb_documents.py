import pandas as pd


INPUT_CSV = "data/tmdb_movies.csv"
OUTPUT_CSV = "data/tmdb_movies_with_documents.csv"


def format_pipe_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return text.replace("|", ", ")


def build_document(row) -> str:
    title = row.get("title", "")
    year = row.get("release_year", "")
    genres = format_pipe_text(row.get("genres", ""))
    overview = row.get("overview", "")
    director = row.get("director", "")
    cast = format_pipe_text(row.get("top_cast", ""))
    keywords = format_pipe_text(row.get("keywords", ""))

    return (
        f"Title: {title} ({year})\n"
        f"Genres: {genres}\n"
        f"Overview: {overview}\n"
        f"Director: {director}\n"
        f"Cast: {cast}\n"
        f"Keywords: {keywords}"
    )


def main():
    df = pd.read_csv(INPUT_CSV)

    df["document"] = df.apply(build_document, axis=1)

    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Saved {len(df)} movies with documents to {OUTPUT_CSV}")
    print("\nExample document:\n")
    print(df.iloc[0]["document"])


if __name__ == "__main__":
    main()