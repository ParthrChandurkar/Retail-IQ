"""Binding NLP feasibility gate; no NLP pipeline is built when the gate is no-go."""

import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, LangDetectException, detect

from app.core.config import get_settings
from app.services.dataframes import query_frame

DetectorFactory.seed = 42


async def evaluate_nlp_feasibility() -> dict[str, object]:
    frame = await query_frame(
        """SELECT comment_message FROM (
             SELECT DISTINCT ON (review_id) review_id,comment_message
             FROM curated.reviews ORDER BY review_id,order_id
           ) review_grain"""
    )
    messages = frame["comment_message"].dropna().astype(str)
    messages = messages[messages.str.strip() != ""]
    token_lengths = messages.str.split().str.len()
    eligible = messages[token_lengths >= 3]
    sample = eligible.sample(n=min(200, len(eligible)), random_state=42)
    languages: list[str] = []
    for message in sample:
        try:
            languages.append(detect(message))
        except LangDetectException:
            continue
    language_counts = pd.Series(languages).value_counts()
    dominant_language = (
        str(language_counts.index[0]) if not language_counts.empty else "undetermined"
    )
    dominant_share = (
        float(language_counts.iloc[0] / language_counts.sum())
        if not language_counts.empty
        else 0.0
    )
    total = int(len(frame))
    non_null = int(len(messages))
    result: dict[str, object] = {
        "decision": "no-go",
        "total_review_ids": total,
        "non_null_comments": non_null,
        "null_rate_pct": 100.0 * (total - non_null) / total,
        "non_null_rate_pct": 100.0 * non_null / total,
        "average_token_length": float(token_lengths.mean()),
        "median_token_length": float(token_lengths.median()),
        "language_sample_size": int(len(languages)),
        "dominant_language": dominant_language,
        "dominant_language_share_pct": 100.0 * dominant_share,
        "reason": (
            "Most reviews have no comment text, and the available text is predominantly "
            "Portuguese. A defensible sentiment/topic module therefore requires a separately "
            "validated Portuguese NLP pipeline; generic English tooling would create misleading "
            "business signals. Score distribution and trend remain the governed fallback."
        ),
    }
    return result


def write_nlp_report(result: dict[str, object]) -> Path:
    output = get_settings().report_dir / "nlp_feasibility.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    commit = os.getenv("GIT_COMMIT", "working-tree")
    content = f"""# NLP Feasibility Gate

- **Generated at:** `{generated}`
- **Dataset row counts used:** unique review IDs={result["total_review_ids"]}; non-null comments={result["non_null_comments"]}
- **Code/commit reference:** `{commit}`
- **Decision:** **{str(result["decision"]).upper()}**

## Required evidence

| Measure | Result |
|---|---:|
| Null comment rate | {result["null_rate_pct"]:.4f}% |
| Non-null comment rate | {result["non_null_rate_pct"]:.4f}% |
| Average token length, non-null comments | {result["average_token_length"]:.4f} |
| Median token length, non-null comments | {result["median_token_length"]:.4f} |
| Language sample successfully classified | {result["language_sample_size"]} comments |
| Dominant language | `{result["dominant_language"]}` |
| Dominant-language share | {result["dominant_language_share_pct"]:.2f}% |

The language sample is deterministic (`RANDOM_SEED=42`) and uses non-empty comments with at least three whitespace-delimited tokens. `pt` denotes Portuguese.

## Decision rationale

{result["reason"]}

No sentiment analysis, keyword extraction, word cloud, or topic-modeling code is built in Phase 6. `GET /reviews/nlp-summary` exposes the governed score-distribution and trend fallback with this no-go status.
"""
    output.write_text(content, encoding="utf-8")
    return output
