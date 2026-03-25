"""Generate a thesis-ready table figure for Likert vs emotion correlation."""

import os
import sys
from collections import Counter
from pathlib import Path
from textwrap import shorten

import django
import matplotlib.pyplot as plt


BASE_PATH = Path(__file__).resolve().parent.parent
if str(BASE_PATH) not in sys.path:
    sys.path.insert(0, str(BASE_PATH))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from api.models import Feedback


def _is_aligned(rating: int, emotions: list[str]) -> bool:
    """Use the same alignment rule used in the revision alignment analysis endpoint."""
    positive_count = emotions.count("joy") + emotions.count("satisfaction")
    negative_count = emotions.count("disappointment") + emotions.count("boredom")
    neutral_count = emotions.count("acceptance")

    if rating >= 4 and positive_count > negative_count:
        return True
    if rating <= 2 and negative_count > positive_count:
        return True
    if rating == 3 and neutral_count >= max(positive_count, negative_count):
        return True
    return False


def _dominant_emotion(emotions: list[str]) -> str:
    """Get the most frequent emotion label from available emotion fields."""
    if not emotions:
        return "N/A"
    return Counter(emotions).most_common(1)[0][0].title()


def _build_interpretation(rating: int, dominant_emotion: str) -> str:
    """Build a concise explanation for why a case may be misaligned."""
    emotion_lower = dominant_emotion.lower()
    negative_emotions = {"disappointment", "boredom"}
    positive_emotions = {"joy", "satisfaction"}

    if rating >= 4 and emotion_lower in negative_emotions:
        return "Possible mixed feedback: student gave a high overall score but described specific pain points in comments."
    if rating <= 2 and emotion_lower in positive_emotions:
        return "Possible contrast effect: positive wording in parts of the response despite a low overall course rating."
    if rating == 3:
        return "Possible ambiguity: neutral score but emotional labels lean away from neutral acceptance."

    return "Likert score and detected emotion signal are inconsistent for this response."


def _pick_comment(feedback: dict) -> str:
    """Select a representative comment snippet for display."""
    candidates = [
        feedback.get("suggested_changes"),
        feedback.get("least_teaching_aspect"),
        feedback.get("further_comments"),
        feedback.get("best_teaching_aspect"),
    ]
    for text in candidates:
        if text and str(text).strip():
            return shorten(str(text).strip().replace("\n", " "), width=90, placeholder="...")
    return "No comment text available"


def build_table_rows(limit: int = 5):
    """Return table rows based on real misaligned-case samples from the system."""
    feedback_rows = Feedback.objects.filter(status="submitted").values(
        "id",
        "overall_rating",
        "suggested_changes",
        "best_teaching_aspect",
        "least_teaching_aspect",
        "further_comments",
        "emotion_suggested_changes",
        "emotion_best_aspect",
        "emotion_least_aspect",
        "emotion_further_comments",
        "course_assignment__course__code",
    )

    rows = []
    for feedback in feedback_rows:
        rating = feedback.get("overall_rating")
        if not rating:
            continue

        emotions = [
            feedback.get("emotion_suggested_changes"),
            feedback.get("emotion_best_aspect"),
            feedback.get("emotion_least_aspect"),
            feedback.get("emotion_further_comments"),
        ]
        emotions = [emotion for emotion in emotions if emotion]
        if not emotions:
            continue

        if _is_aligned(rating, emotions):
            continue

        course_code = feedback.get("course_assignment__course__code") or "Unknown"
        dominant = _dominant_emotion(emotions)
        interpretation = _build_interpretation(rating, dominant)
        comment = _pick_comment(feedback)
        rows.append([
            course_code,
            f"{float(rating):.1f}",
            dominant,
            comment,
            interpretation,
        ])

    if not rows:
        return [["No data", "-", "-", "-", "No misaligned cases found in submitted feedback"]]

    return rows[:limit]


def generate_table_figure(output_file: Path) -> None:
    """Render and save the table visualization as a PNG file."""
    columns = ["Course", "Likert Rating", "Dominant Emotion", "Comment", "Interpretation"]
    rows = build_table_rows(limit=5)

    fig, ax = plt.subplots(figsize=(18, 5.2), dpi=200)
    ax.axis("off")

    fig.suptitle(
        "Table X. Correlation Between Likert Ratings and Emotion Classification",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    table = ax.table(
        cellText=rows,
        colLabels=columns,
        loc="center",
        cellLoc="left",
        colLoc="left",
        colWidths=[0.1, 0.1, 0.14, 0.28, 0.38],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    header_color = "#8E1B1B"
    stripe_color = "#F9FAFB"
    border_color = "#D1D5DB"

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        cell.set_linewidth(0.8)

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor(stripe_color)

    fig.tight_layout(rect=[0.01, 0.02, 0.99, 0.9])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    base_path = Path(__file__).resolve().parent.parent
    output_dir = base_path / "data" / "annotations" / "visualizations"
    output_file = output_dir / "likert_emotion_correlation_table.png"

    generate_table_figure(output_file)
    print(f"Generated: {output_file}")


if __name__ == "__main__":
    main()
