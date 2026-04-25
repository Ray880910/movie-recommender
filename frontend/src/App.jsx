import { useState } from "react";
import "./App.css";

import ChatRecommendBox from "./components/ChatRecommendBox";
import ChatRecommendationSection from "./components/ChatRecommendationSection";

function App() {
  const [chatMessage, setChatMessage] = useState("");
  const [chatResult, setChatResult] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  // 多輪狀態
  const [history, setHistory] = useState([]);
  const [shownMovieIds, setShownMovieIds] = useState([]);
  const [likes, setLikes] = useState([]);
  const [dislikes, setDislikes] = useState([]);

  // 對話紀錄（前端顯示用）
  const [conversation, setConversation] = useState([]);

  const getChatRecommendations = async () => {
    setChatError("");
    setChatResult(null);

    if (!chatMessage.trim()) {
      setChatError("請輸入你想看的電影描述");
      return;
    }

    const currentMessage = chatMessage.trim();

    try {
      setChatLoading(true);

      const response = await fetch("http://127.0.0.1:8000/chat-recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentMessage,
          history: history,
          shown_movie_ids: shownMovieIds,
          likes: likes,
          dislikes: dislikes,
        }),
      });

      if (!response.ok) {
        throw new Error("AI 推薦失敗");
      }

      const data = await response.json();
      setChatResult(data);

      // 更新對話紀錄
      setConversation((prev) => [
        ...prev,
        {
          role: "user",
          content: currentMessage,
        },
        {
          role: "assistant",
          content: data.explanation,
          recommendations: data.recommendations || [],
        },
      ]);

      // 更新 history（只記 user 的話）
      setHistory((prev) => [...prev, currentMessage]);

      // 更新已推薦電影 id
      const newIds = (data.recommendations || []).map((movie) => movie.movieId);
      setShownMovieIds((prev) => [...prev, ...newIds]);

      // 清空輸入框
      setChatMessage("");
    } catch (err) {
      setChatError(err.message || "發生錯誤");
    } finally {
      setChatLoading(false);
    }
  };

  const resetConversation = () => {
    setChatMessage("");
    setChatResult(null);
    setChatError("");
    setHistory([]);
    setShownMovieIds([]);
    setLikes([]);
    setDislikes([]);
    setConversation([]);
  };

  return (
    <div className="page">
      <div className="container">
        <header className="hero">
          <h1>Semantic Movie Recommender</h1>
          <p>
            直接輸入你想看的電影風格，系統會根據你的多輪回饋持續調整推薦結果。
          </p>
        </header>

        <section className="section">
          <div className="section-header">
            <h2>電影推薦對話</h2>
            <button className="reset-button" onClick={resetConversation}>
              清除對話
            </button>
          </div>

          <ChatRecommendBox
            chatMessage={chatMessage}
            setChatMessage={setChatMessage}
            onSubmit={getChatRecommendations}
            loading={chatLoading}
          />

          {chatLoading && <div className="status loading">推薦中...</div>}
          {chatError && <div className="status error">{chatError}</div>}

          {conversation.length > 0 && (
            <div className="conversation-section">
              {conversation.map((item, index) => (
                <div
                  key={index}
                  className={
                    item.role === "user"
                      ? "chat-bubble user-bubble"
                      : "chat-bubble assistant-bubble"
                  }
                >
                  {item.role === "user" ? (
                    <>
                      <div className="chat-role">You</div>
                      <p>{item.content}</p>
                    </>
                  ) : (
                    <>
                      <div className="chat-role">AI Recommender</div>
                      <p>{item.content}</p>

                      {item.recommendations && item.recommendations.length > 0 && (
                        <ChatRecommendationSection
                          chatResult={{ recommendations: item.recommendations }}
                        />
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;