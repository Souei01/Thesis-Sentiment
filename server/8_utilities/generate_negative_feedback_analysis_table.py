"""Generate Negative Feedback Analysis table outputs from system data."""

import html
import os
import sys
from collections import Counter
from pathlib import Path
from textwrap import fill

import django
import matplotlib.pyplot as plt


BASE_PATH = Path(__file__).resolve().parent.parent
if str(BASE_PATH) not in sys.path:
    sys.path.insert(0, str(BASE_PATH))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from api.models import Feedback


def normalize_text(value: str | None) -> str:
    """Normalize text for readable display in table outputs."""
    if not value:
        return ""
    text = html.unescape(str(value)).replace("\r", " ").replace("\n", " ").strip()
    return " ".join(text.split())


def choose_student_feedback(feedback: dict) -> tuple[str, str, str]:
    """Pick feedback text and return (question_source, text, matched_emotion)."""
    candidates = [
        ("Least Teaching Aspect", "least_teaching_aspect", "emotion_least_aspect"),
        ("Suggested Changes", "suggested_changes", "emotion_suggested_changes"),
        ("Further Comments", "further_comments", "emotion_further_comments"),
        ("Best Teaching Aspect", "best_teaching_aspect", "emotion_best_aspect"),
    ]

    for question_label, text_field, emotion_field in candidates:
        text = normalize_text(feedback.get(text_field))
        if text:
            emotion = normalize_text(feedback.get(emotion_field)).title() or "N/A"
            return question_label, text, emotion

    return "N/A", "No comment text provided", "N/A"


def dominant_emotion(feedback: dict) -> str:
    """Get dominant emotion from available emotion fields."""
    emotions = [
        feedback.get("emotion_suggested_changes"),
        feedback.get("emotion_best_aspect"),
        feedback.get("emotion_least_aspect"),
        feedback.get("emotion_further_comments"),
    ]
    emotions = [str(e).strip().lower() for e in emotions if e and str(e).strip()]
    if not emotions:
        return "N/A"
    return Counter(emotions).most_common(1)[0][0].title()


def identify_issue(comment: str) -> str:
    """Assign issue category based on keyword hits in the student feedback text."""
    text = comment.lower()

    issue_keywords = {
        "Teaching Methods": ["teach", "explain", "lecture", "clarity", "understand", "instructor"],
        "Course Materials": ["material", "module", "book", "slides", "resource", "handout"],
        "Assessment": ["exam", "quiz", "test", "grade", "grading", "assessment", "rubric"],
        "Workload": ["workload", "assignment", "homework", "deadline", "too much", "overwhelming"],
        "Communication/Availability": ["communicate", "respond", "reply", "meet", "meeting", "absent", "available"],
        "Engagement": ["boring", "engage", "interactive", "interest", "dull", "monotonous", "fun"],
    }

    for issue, keywords in issue_keywords.items():
        if any(keyword in text for keyword in keywords):
            return issue

    return "General Dissatisfaction"


def fetch_negative_feedback_rows() -> list[list[str]]:
    """Fetch all negative feedback rows (1-2 stars) and map them to table columns."""
    qs = Feedback.objects.filter(status="submitted", overall_rating__lte=2).values(
        "overall_rating",
        "course_assignment__course__code",
        "suggested_changes",
        "best_teaching_aspect",
        "least_teaching_aspect",
        "further_comments",
        "emotion_suggested_changes",
        "emotion_best_aspect",
        "emotion_least_aspect",
        "emotion_further_comments",
    )

    rows: list[list[str]] = []
    for feedback in qs:
        course = feedback.get("course_assignment__course__code") or "Unknown"
        question_source, comment, matched_emotion = choose_student_feedback(feedback)
        emotion = matched_emotion if matched_emotion != "N/A" else dominant_emotion(feedback)
        issue = identify_issue(comment)
        rows.append([course, question_source, emotion, comment, issue])

    return rows


def write_txt_table(output_file: Path, columns: list[str], rows: list[list[str]]) -> None:
    """Write a plain-text table file for thesis documentation."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    widths = [len(col) for col in columns]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    # Keep txt readable by capping wide feedback column; wrap long values.
    widths = [min(widths[0], 18), min(widths[1], 26), min(widths[2], 20), 90, min(widths[4], 35)]

    def format_row(values: list[str]) -> str:
        return " | ".join(
            values[i].ljust(widths[i]) if i != 2 else values[i].ljust(widths[i])
            for i in range(len(values))
        )

    separator = "-+-".join("-" * w for w in widths)

    with output_file.open("w", encoding="utf-8") as f:
        f.write("Table X. Sample Negative Feedback and Identified Issues\n")
        f.write("\n")
        f.write(format_row(columns) + "\n")
        f.write(separator + "\n")

        for row in rows:
            wrapped_comment = fill(row[3], width=widths[3]).split("\n")
            first_line = [row[0], row[1], row[2], wrapped_comment[0], row[4]]
            f.write(format_row(first_line) + "\n")
            for cont_line in wrapped_comment[1:]:
                f.write(format_row(["", "", "", cont_line, ""]) + "\n")


def generate_png_table(output_file: Path, columns: list[str], rows: list[list[str]]) -> None:
    """Render the negative feedback table as a Matplotlib PNG figure."""
    display_rows = [[r[0], r[1], r[2], fill(r[3], width=55), r[4]] for r in rows]

    n_rows = max(1, len(display_rows))
    fig_height = max(6, min(36, 1.2 + (n_rows + 1) * 0.5))

    fig, ax = plt.subplots(figsize=(24, fig_height), dpi=180)
    ax.axis("off")

    fig.suptitle(
        "Table X. Sample Negative Feedback and Identified Issues",
        fontsize=14,
        fontweight="bold",
        y=0.995,
    )

    table = ax.table(
        cellText=display_rows if display_rows else [["No data", "-", "-", "No negative feedback found", "-"]],
        colLabels=columns,
        loc="center",
        cellLoc="left",
        colLoc="left",
        colWidths=[0.1, 0.16, 0.11, 0.45, 0.18],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)

    header_color = "#8E1B1B"
    stripe_color = "#F9FAFB"
    border_color = "#D1D5DB"

    for (row_idx, _col_idx), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        cell.set_linewidth(0.7)

        if row_idx == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        elif row_idx % 2 == 0:
            cell.set_facecolor(stripe_color)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0.01, 0.01, 0.99, 0.975])
    fig.savefig(output_file, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    output_dir = BASE_PATH / "data" / "annotations" / "visualizations"
    png_out = output_dir / "negative_feedback_analysis_table.png"
    txt_out = output_dir / "negative_feedback_analysis_table.txt"

    columns = ["Course", "Question", "Emotion", "Student Feedback", "Identified Issue"]
    rows = fetch_negative_feedback_rows()

    write_txt_table(txt_out, columns, rows)
    generate_png_table(png_out, columns, rows)

    print(f"Generated: {png_out}")
    print(f"Generated: {txt_out}")
    print(f"Rows included: {len(rows)}")


if __name__ == "__main__":
    main()
