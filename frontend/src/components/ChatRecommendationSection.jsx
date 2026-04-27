function ChatRecommendationSection({ chatResult }) {
  if (!chatResult || !chatResult.recommendations) return null;

  return (
    <div style={{ marginTop: "16px" }}>
      <div className="section-header">
        <h3>推薦結果</h3>
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
                <h4>
                  {movie.title_zh && movie.title_zh !== movie.title ? (
                    <>
                      {movie.title_zh}
                      <br />
                      <span className="original-title">
                        {movie.title}
                        {movie.release_year && ` (${movie.release_year})`}
                      </span>
                    </>
                  ) : (
                    <>
                      {movie.title}
                      {movie.release_year && ` (${movie.release_year})`}
                    </>
                  )}
                </h4>

                <p className="genres">
                  {movie.genres?.replaceAll("|", " • ")}
                </p>

                {movie.director && (
                  <p className="meta">
                    <strong>導演：</strong>{movie.director}
                  </p>
                )}

                {movie.top_cast && (
                  <p className="meta">
                    <strong>主要演員：</strong>
                    {movie.top_cast.replaceAll("|", "、")}
                  </p>
                )}

                <p className="meta">
                  <strong>評分：</strong>
                  {movie.vote_average !== null && movie.vote_average !== undefined
                    ? Number(movie.vote_average).toFixed(1)
                    : "N/A"}
                  {" / 10"}
                </p>

                <p className="meta">
                  <strong>評分數：</strong>
                  {movie.vote_count ?? "N/A"}
                </p>

                {movie.final_score !== null && movie.final_score !== undefined && (
                  <p className="score">
                    Recommendation Score: {Number(movie.final_score).toFixed(4)}
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