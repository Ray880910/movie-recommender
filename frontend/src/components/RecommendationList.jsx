function RecommendationList({ recommendations }) {
  if (recommendations.length === 0) {
    return <div className="empty-box">目前沒有推薦結果</div>;
  }

  return (
    <div className="recommendation-list">
      {recommendations.map((movie, index) => (
        <div className="recommendation-card" key={movie.movieId}>
          <div className="rank-badge">{index + 1}</div>
          <div className="recommendation-content">
            <h3>{movie.title}</h3>
                <p className="genres">
                    {movie.genres.replaceAll("|", " • ")}
                </p>
            <p className="score">
              Score: {Number(movie.final_score).toFixed(4)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default RecommendationList;