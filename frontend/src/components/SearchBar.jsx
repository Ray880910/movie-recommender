function SearchBar({ keyword, setKeyword, onSearch }) {
  return (
    <div className="search-panel">
      <input
        className="search-input"
        type="text"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="例如 Toy Story"
        onKeyDown={(e) => {
          if (e.key === "Enter") onSearch();
        }}
      />
      <button className="search-button" onClick={onSearch}>
        搜尋
      </button>
    </div>
  );
}

export default SearchBar;