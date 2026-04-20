import { useState } from "react";
import "./App.css";

import ChatRecommendBox from "./components/ChatRecommendBox";
import ChatRecommendationSection from "./components/ChatRecommendationSection";

function App() {
  const [chatMessage, setChatMessage] = useState("");
  const [chatResult, setChatResult] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

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

  return (
    <div className="page">
      <div className="container">
        <header className="hero">
          <h1>Semantic Movie Recommender</h1>
          <p>直接輸入你想看的電影風格，系統會用語意搜尋推薦最接近的電影。</p>
        </header>

        <section className="section">
          <div className="section-header">
            <h2>電影推薦</h2>
          </div>

          <ChatRecommendBox
            chatMessage={chatMessage}
            setChatMessage={setChatMessage}
            onSubmit={getChatRecommendations}
            loading={chatLoading}
          />

          {chatLoading && <div className="status loading">推薦中...</div>}
          {chatError && <div className="status error">{chatError}</div>}

          {chatResult && (
            <div className="chat-result">
              <div className="selected-card" style={{ marginTop: "16px" }}>
                <h3>Recommendation Explanation</h3>
                <p>{chatResult.explanation}</p>
              </div>

              <ChatRecommendationSection chatResult={chatResult} />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;