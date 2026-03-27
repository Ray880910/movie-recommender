function ParsedPreferencesCard({ chatResult }) {
  if (!chatResult) return null;

  const prefs = chatResult.parsed_preferences;

  return (
    <>
      <div className="selected-card">
        <h3>AI 理解的偏好</h3>
        <p>
          <strong>Reference Titles：</strong>{" "}
          {prefs.reference_titles.length > 0
            ? prefs.reference_titles.join(", ")
            : "無"}
        </p>
        <p>
          <strong>Genres：</strong>{" "}
          {prefs.genres.length > 0 ? prefs.genres.join(", ") : "無"}
        </p>
        <p>
          <strong>Mood：</strong>{" "}
          {prefs.mood.length > 0 ? prefs.mood.join(", ") : "無"}
        </p>
        <p>
          <strong>Exclude：</strong>{" "}
          {prefs.exclude.length > 0 ? prefs.exclude.join(", ") : "無"}
        </p>
      </div>

      {chatResult.seed_movie && (
        <div className="selected-card" style={{ marginTop: "16px" }}>
          <h3>Seed Movie</h3>
          <p>
            <strong>{chatResult.seed_movie.title}</strong>
            <br />
            <span className="genres">
              {chatResult.seed_movie.genres.replaceAll("|", " • ")}
            </span>
          </p>
        </div>
      )}

      <div className="selected-card" style={{ marginTop: "16px" }}>
        <h3>AI Explanation</h3>
        <p>{chatResult.explanation}</p>
      </div>
    </>
  );
}

export default ParsedPreferencesCard;