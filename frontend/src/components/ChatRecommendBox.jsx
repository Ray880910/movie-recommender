function ChatRecommendBox({ chatMessage, setChatMessage, onSubmit, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="chat-box">
      <textarea
        value={chatMessage}
        onChange={(e) => setChatMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="例如：我想看溫馨的動畫電影。下一輪可以再說：更冒險一點，不要太悲傷。"
        rows={4}
      />
      <button onClick={onSubmit} disabled={loading}>
        {loading ? "推薦中..." : "送出"}
      </button>
    </div>
  );
}

export default ChatRecommendBox;