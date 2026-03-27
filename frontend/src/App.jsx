import { useState } from "react";
import "./App.css";

import SearchBar from "./components/SearchBar";
import MovieCard from "./components/MovieCard";
import RecommendationList from "./components/RecommendationList";
import ChatRecommendBox from "./components/ChatRecommendBox";
import ParsedPreferencesCard from "./components/ParsedPreferencesCard";
import ChatRecommendationSection from "./components/ChatRecommendationSection";

function App() {
  const [keyword, setKeyword] = useState("");
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [chatMessage, setChatMessage] = useState("");
  const [chatResult, setChatResult] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  const searchMovies = async () => {
    setError("");
    setRecommendations([]);
    setSelectedMovie(null);
    setMovies([]);

    if (!keyword.trim()) {
      setError("請輸入電影名稱");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        `http://127.0.0.1:8000/movies/search?keyword=${encodeURIComponent(keyword)}`
      );

      if (!response.ok) {
        throw new Error("搜尋失敗");
      }

      const data = await response.json();
      setMovies(data.results || []);
    } catch (err) {
      setError(err.message || "發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  const getChatRecommendations = async () => {
    setChatError("");
    setChatResult(null);

    if (!chatMessage.trim()) {
      setChatError("請輸入你想看的電影描述");
      return;
    }

    try {
      setChatLoading(true);

      const response = await fetch("http://127.0.0.1:8000/chat-recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: chatMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("AI 推薦失敗");
      }

      const data = await response.json();
      setChatResult(data);
    } catch (err) {
      setChatError(err.message || "發生錯誤");
    } finally {
      setChatLoading(false);
    }
  };

  const getRecommendations = async (movie) => {
    setError("");
    setSelectedMovie(movie);
    setRecommendations([]);

    try {
      setLoading(true);
      const response = await fetch(
        `http://127.0.0.1:8000/recommend?movie_id=${movie.movieId}`
      );

      if (!response.ok) {
        throw new Error("取得推薦失敗");
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError(err.message || "發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <header className="hero">
          <h1>Movie Recommender</h1>
          <p>輸入電影名稱，搜尋電影後查看推薦結果。</p>
        </header>

        {/* AI 推薦區 */}
        <section className="section">
          <div className="section-header">
            <h2>AI 推薦</h2>
          </div>

          <ChatRecommendBox
            chatMessage={chatMessage}
            setChatMessage={setChatMessage}
            onSubmit={getChatRecommendations}
            loading={chatLoading}
          />

          {chatLoading && <div className="status loading">AI 推薦中...</div>}
          {chatError && <div className="status error">{chatError}</div>}

          {chatResult && (
            <div className="chat-result">
              <ParsedPreferencesCard chatResult={chatResult} />
              <ChatRecommendationSection chatResult={chatResult} />
            </div>
          )}
        </section>

        {/* 一般搜尋 */}
        <SearchBar
          keyword={keyword}
          setKeyword={setKeyword}
          onSearch={searchMovies}
        />

        {loading && <div className="status loading">載入中...</div>}
        {error && <div className="status error">{error}</div>}

        <section className="section">
          <div className="section-header">
            <h2>搜尋結果</h2>
            <span>{movies.length} 筆</span>
          </div>

          {movies.length === 0 ? (
            <div className="empty-box">目前沒有搜尋結果</div>
          ) : (
            <div className="movie-grid">
              {movies.map((movie) => (
                <MovieCard
                  key={movie.movieId}
                  movie={movie}
                  onSelect={getRecommendations}
                />
              ))}
            </div>
          )}
        </section>

        {selectedMovie && (
          <section className="section">
            <div className="section-header">
              <h2>目前選擇</h2>
            </div>
            <div className="selected-card">
              <h3>{selectedMovie.title}</h3>
              <p className="genres">
                {selectedMovie.genres.replaceAll("|", " • ")}
              </p>
            </div>
          </section>
        )}

        <section className="section">
          <div className="section-header">
            <h2>推薦結果</h2>
            <span>{recommendations.length} 筆</span>
          </div>

          <RecommendationList recommendations={recommendations} />
        </section>
      </div>
    </div>
  );
}

export default App;