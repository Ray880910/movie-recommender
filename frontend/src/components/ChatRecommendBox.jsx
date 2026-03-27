function ChatRecommendBox({
  chatMessage,
  setChatMessage,
  onSubmit,
  loading,
}) {
  return (
    <div className="chat-panel">
      <textarea
        className="chat-input"
        value={chatMessage}
        onChange={(e) => setChatMessage(e.target.value)}
        placeholder="例如：我想看像 Inception 的電影，或推薦溫馨的動畫電影"
        rows={4}
      />
      <button
        className="search-button"
        onClick={onSubmit}
        disabled={loading}
      >
        {loading ? "AI 推薦中..." : "讓 AI 推薦"}
      </button>
    </div>
  );
}

export default ChatRecommendBox;