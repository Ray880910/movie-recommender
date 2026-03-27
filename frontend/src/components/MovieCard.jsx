function MovieCard({ movie, onSelect }) {
  return (
    <div className="movie-card">
      <div className="movie-card-body">
        <h3>{movie.title}</h3>
            <p className="genres">
                {movie.genres.replaceAll("|", " • ")}
            </p>
      </div>
      <button
        className="card-button"
        onClick={() => onSelect(movie)}
      >
        查看推薦
      </button>
    </div>
  );
}

export default MovieCard;