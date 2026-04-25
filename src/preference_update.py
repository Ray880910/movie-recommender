import json
import os
from typing import Dict, List

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def normalize_terms(terms: List[str]) -> List[str]:
    seen = set()
    result = []

    for term in terms:
        cleaned = term.strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)

    return result


def apply_preference_actions(
    current_likes: List[str],
    current_dislikes: List[str],
    actions: Dict,
) -> Dict[str, List[str] | str]:
    likes = normalize_terms(current_likes)
    dislikes = normalize_terms(current_dislikes)

    likes_to_add = normalize_terms(actions.get("likes_to_add", []))
    likes_to_remove = normalize_terms(actions.get("likes_to_remove", []))
    dislikes_to_add = normalize_terms(actions.get("dislikes_to_add", []))
    dislikes_to_remove = normalize_terms(actions.get("dislikes_to_remove", []))
    shift_type = actions.get("shift_type", "unknown")

    likes = [term for term in likes if term not in likes_to_remove]
    dislikes = [term for term in dislikes if term not in dislikes_to_remove]

    likes = normalize_terms(likes + likes_to_add)
    dislikes = normalize_terms(dislikes + dislikes_to_add)

    # 避免同一個詞同時存在 likes 和 dislikes
    dislikes = [term for term in dislikes if term not in likes]

    return {
        "likes": likes,
        "dislikes": dislikes,
        "shift_type": shift_type,
    }


def parse_preference_actions_with_llm(
    message: str,
    current_likes: List[str],
    current_dislikes: List[str],
) -> Dict:
    prompt = f"""
You are a preference update planner for a conversational movie recommendation system.

Current state:
likes = {current_likes}
dislikes = {current_dislikes}

User message:
{message}

Your task:
Decide how the preference state should be updated.

Return update actions, not the final state.

Rules:
- If the user adds a new preference, put it in likes_to_add.
- If the user says "too", "also", "as well", or similar, preserve existing likes.
- If the user clearly replaces previous preferences using "instead", "rather than", "switch to", "change to", etc., put conflicting old likes in likes_to_remove and dislikes_to_add.
- If the user says they do not want something, put it in dislikes_to_add and likes_to_remove.
- If the user says they still like something, do not remove it.
- Keep terms short and useful for movie recommendation: genres, moods, themes, directors, actors, or styles.
- Do not invent unnecessary preferences.
- Output JSON only.

Allowed shift_type values:
- "new_preference"
- "supplement"
- "minor_refinement"
- "strong_shift"
- "negative_constraint"
- "unknown"

Output format:
{{
  "shift_type": "strong_shift",
  "likes_to_add": ["sci-fi"],
  "likes_to_remove": ["animation"],
  "dislikes_to_add": ["animation"],
  "dislikes_to_remove": []
}}
""".strip()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    text = response.output_text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    print("[DEBUG] LLM preference action output:", text)

    return json.loads(text)


def update_preferences(
    message: str,
    current_likes: List[str],
    current_dislikes: List[str],
) -> Dict[str, List[str] | str]:
    try:
        actions = parse_preference_actions_with_llm(
            message=message,
            current_likes=current_likes,
            current_dislikes=current_dislikes,
        )

        updated = apply_preference_actions(
            current_likes=current_likes,
            current_dislikes=current_dislikes,
            actions=actions,
        )

        updated["update_source"] = "llm_action"

        print("[INFO] Preference update source: LLM action")
        print("[INFO] Updated preferences:", updated)

        return updated

    except Exception as e:
        print("[WARN] LLM preference action failed:", e)

        return {
            "likes": normalize_terms(current_likes),
            "dislikes": normalize_terms(current_dislikes),
            "shift_type": "fallback_failed",
            "update_source": "fallback_keep_current",
        }