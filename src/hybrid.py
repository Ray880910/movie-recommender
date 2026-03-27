import pandas as pd


def recommend_hybrid(
    movie_id: int,
    collaborative_similarity_df: pd.DataFrame,
    content_similarity_df: pd.DataFrame,
    movies: pd.DataFrame,
    top_n: int = 10,
    alpha: float = 0.7,
):
    if movie_id not in collaborative_similarity_df.index:
        return pd.DataFrame()

    if movie_id not in content_similarity_df.index:
        return pd.DataFrame()

    # 取出 collaborative 分數
    collaborative_scores = collaborative_similarity_df[movie_id].rename("collaborative_score")

    # 取出 content-based 分數
    content_scores = content_similarity_df[movie_id].rename("content_score")

    # 合併兩組分數
    scores_df = pd.concat([collaborative_scores, content_scores], axis=1).fillna(0)

    # 不推薦自己
    scores_df = scores_df.drop(movie_id, errors="ignore")

    # 計算最終分數
    scores_df["final_score"] = (
        alpha * scores_df["collaborative_score"]
        + (1 - alpha) * scores_df["content_score"]
    )

    # 排序
    scores_df = scores_df.sort_values(by="final_score", ascending=False).head(top_n)

    # 合併電影資訊
    result = movies[movies["movieId"].isin(scores_df.index)].copy()
    result["collaborative_score"] = result["movieId"].map(scores_df["collaborative_score"])
    result["content_score"] = result["movieId"].map(scores_df["content_score"])
    result["final_score"] = result["movieId"].map(scores_df["final_score"])

    result = result.sort_values(by="final_score", ascending=False)

    return result[
        ["movieId", "title", "genres", "collaborative_score", "content_score", "final_score"]
    ]