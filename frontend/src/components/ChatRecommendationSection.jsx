function ChatRecommendationSection({ chatResult }) {
  if (!chatResult) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <div className="section-header">
        <h2>推薦結果</h2>
        <span>{chatResult.recommendations.length} 筆</span>
      </div>

      {chatResult.recommendations.length === 0 ? (
        <div className="empty-box">目前沒有推薦結果</div>
      ) : (
        <div className="recommendation-list">
          {chatResult.recommendations.map((movie, index) => (
            <div className="recommendation-card" key={movie.movieId}>
              <div className="rank-badge">{index + 1}</div>
              <div className="recommendation-content">
                <h3>{movie.title}</h3>
                <p className="genres">
                  {movie.genres.replaceAll("|", " • ")}
                </p>
                {movie.final_score !== null && (
                  <p className="score">
                    Score: {Number(movie.final_score).toFixed(4)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChatRecommendationSection;