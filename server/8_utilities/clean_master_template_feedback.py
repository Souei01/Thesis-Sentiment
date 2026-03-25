from pathlib import Path

import pandas as pd


VALID_EMOTIONS = {'joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment'}
NULL_LIKE = {'', 'nan', 'none', 'null', 'n/a', 'na'}


def normalize_text(value) -> str:
    if value is None:
        return ''
    text = str(value).strip().lower()
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = ' '.join(text.split())
    return text


def normalize_label(value) -> str:
    val = normalize_text(value)
    if val in NULL_LIKE:
        return 'null'
    return val


def extract_text_label_pairs(df: pd.DataFrame):
    cols = list(df.columns)
    pairs = []
    for i, col in enumerate(cols):
        col_norm = str(col).strip().lower()
        if col_norm.startswith('label'):
            continue
        nxt = cols[i + 1] if i + 1 < len(cols) else None
        if nxt and str(nxt).strip().lower().startswith('label'):
            pairs.append((col, nxt))
    return pairs


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    ann_dir = base_dir / 'data' / 'annotations'

    src = ann_dir / 'Student Feedback Sentiment Annotation Form - Master Template.csv'
    out_long = ann_dir / 'master_template_cleaned_long.csv'

    raw = pd.read_csv(src)
    pairs = extract_text_label_pairs(raw)

    rows = []
    removed_null_or_irrelevant = 0
    removed_empty_feedback = 0

    for ridx, row in raw.iterrows():
        respondent_id = ridx + 1
        for qidx, (text_col, label_col) in enumerate(pairs, start=1):
            feedback_text = str(row.get(text_col, '')).strip()
            feedback_norm = normalize_text(feedback_text)
            label = normalize_label(row.get(label_col, 'null'))

            if feedback_norm in NULL_LIKE:
                removed_empty_feedback += 1
                continue

            if label not in VALID_EMOTIONS:
                removed_null_or_irrelevant += 1
                continue

            rows.append(
                {
                    'feedback_id': f'q{qidx}_f{respondent_id}',
                    'respondent_id': respondent_id,
                    'question_num': qidx,
                    'student_feedback': feedback_text,
                    'ai_label': label,
                }
            )

    cleaned = pd.DataFrame(rows)
    cleaned.to_csv(out_long, index=False, encoding='utf-8')

    print(f'Generated: {out_long}')
    print(f'Rows kept: {len(cleaned)}')
    print(f'Removed (empty feedback): {removed_empty_feedback}')
    print(f'Removed (null/irrelevant labels): {removed_null_or_irrelevant}')


if __name__ == '__main__':
    main()
