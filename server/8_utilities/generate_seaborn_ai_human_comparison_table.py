from collections import Counter
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


VALID_EMOTIONS = {'joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment'}
QUESTION_LABELS = {
    1: 'Course Improvement',
    2: 'Best Teaching Aspect',
    3: 'Least Teaching Aspect',
    4: 'Further Comment',
}


def normalize_text(value: str) -> str:
    if value is None:
        return ''
    text = str(value).strip().lower()
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = ' '.join(text.split())
    return text


def normalize_label(value: str) -> str:
    val = normalize_text(value)
    if val in {'', 'nan', 'none', 'null', 'n/a'}:
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


def flatten_master_template(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    pairs = extract_text_label_pairs(raw)

    rows = []
    for ridx, row in raw.iterrows():
        respondent_id = ridx + 1
        for qidx, (text_col, label_col) in enumerate(pairs, start=1):
            text = str(row.get(text_col, '')).strip()
            ai_label = normalize_label(row.get(label_col, 'null'))
            feedback_id = f'q{qidx}_f{respondent_id}'
            rows.append(
                {
                    'feedback_id': feedback_id,
                    'student_feedback': text,
                    'ai_label': ai_label,
                    'question_num': qidx,
                }
            )

    return pd.DataFrame(rows)


def human_majority_label(row: pd.Series) -> str:
    labels = [
        normalize_label(row.get('annotator_1', 'null')),
        normalize_label(row.get('annotator_2', 'null')),
        normalize_label(row.get('annotator_3', 'null')),
    ]
    labels = [x for x in labels if x in VALID_EMOTIONS]
    if not labels:
        return 'null'

    counts = Counter(labels)
    most_common = counts.most_common()
    max_count = most_common[0][1]
    tied = sorted([lbl for lbl, cnt in most_common if cnt == max_count])
    return tied[0]


def build_observation(human_label: str, ai_label: str, feedback_text: str, question_label: str) -> str:
    text = normalize_text(feedback_text)

    if human_label == ai_label:
        return 'Human and AI labels are aligned for this response.'

    positive = {'joy', 'satisfaction'}
    negative = {'boredom', 'disappointment'}
    complaint_terms = {
        'lack', 'late', 'hard', 'difficult', 'boring', 'strict', 'overwhelming',
        'deadline', 'busy', 'problem', 'issue', 'fair', 'failing', 'nothing'
    }
    praise_terms = {
        'good', 'great', 'excellent', 'helpful', 'clear', 'fun', 'engaging',
        'knowledge', 'best', 'appreciate', 'understand'
    }

    has_complaint_cues = any(term in text for term in complaint_terms)
    has_praise_cues = any(term in text for term in praise_terms)

    if human_label in positive and ai_label in positive:
        return (
            f"Human annotation indicates {human_label} while AI assigns {ai_label}; "
            'both are positive, but the intensity/subtype differs.'
        )
    if human_label in negative and ai_label in negative:
        return (
            f"Human annotation indicates {human_label} while AI assigns {ai_label}; "
            'both are negative, but they emphasize different negative tones.'
        )
    if human_label == 'acceptance' and ai_label in positive.union(negative):
        if has_complaint_cues or has_praise_cues:
            return (
                f"In {question_label}, human coders treated the response as acceptance, "
                f"while AI classified it as {ai_label} due to explicit sentiment-bearing words."
            )
        return (
            f"In {question_label}, human coders assigned acceptance, "
            f"whereas AI assigned {ai_label}; the difference likely comes from subtle tone interpretation."
        )
    if ai_label == 'acceptance' and human_label in positive.union(negative):
        if has_complaint_cues or has_praise_cues:
            return (
                f"In {question_label}, AI reduced the response to acceptance, "
                f"while human coders labeled {human_label}; lexical cues indicate stronger sentiment than neutral."
            )
        return (
            f"In {question_label}, AI assigned acceptance but human coders labeled {human_label}; "
            'this reflects weaker AI sensitivity to contextual tone.'
        )
    if ai_label == 'null':
        return 'AI label is missing/invalid, while human annotation provides a valid emotion class.'

    if human_label in positive and ai_label in negative:
        return (
            f"Human coders labeled the response as {human_label}, but AI labeled it {ai_label}; "
            'polarity was reversed, likely because positive and critical cues co-occur in the same text.'
        )
    if human_label in negative and ai_label in positive:
        return (
            f"Human coders labeled the response as {human_label}, but AI labeled it {ai_label}; "
            'polarity was reversed, likely because isolated positive words outweighed critical context for the model.'
        )

    return (
        f"Human coders assigned {human_label}, while AI assigned {ai_label}; "
        'the divergence reflects different weighting of semantics and discourse context.'
    )


def wrap_for_table(text: str, width: int) -> str:
    txt = str(text).strip()
    if not txt:
        return ''
    return '\n'.join(textwrap.wrap(txt, width=width))


def render_seaborn_table(df: pd.DataFrame, output_png: Path) -> None:
    display_df = df.copy()
    display_df['student_feedback'] = display_df['student_feedback'].apply(lambda x: wrap_for_table(x, 42))
    display_df['question'] = display_df['question'].apply(lambda x: wrap_for_table(x, 24))
    display_df['human_label'] = display_df['human_label'].str.capitalize()
    display_df['ai_label'] = display_df['ai_label'].str.capitalize()
    display_df['observation'] = display_df['observation'].apply(lambda x: wrap_for_table(x, 42))

    rows = len(display_df)
    cols = 5

    # Color grid values: use stronger value on agreement rows for the observation column.
    matrix = np.full((rows, cols), 0.35)
    agreement_mask = display_df['human_label'].str.lower() == display_df['ai_label'].str.lower()
    matrix[:, 0] = 0.30
    matrix[:, 1] = 0.25
    matrix[:, 2] = np.where(agreement_mask, 0.75, 0.45)
    matrix[:, 3] = np.where(agreement_mask, 0.75, 0.45)
    matrix[:, 4] = np.where(agreement_mask, 0.90, 0.20)

    annot = np.array(
        display_df[['question', 'student_feedback', 'human_label', 'ai_label', 'observation']].values,
        dtype=object,
    )

    sns.set_theme(style='white', context='paper')
    fig_height = max(8, rows * 0.9)
    fig, ax = plt.subplots(figsize=(23, fig_height), dpi=220)

    sns.heatmap(
        matrix,
        annot=annot,
        fmt='',
        cmap='RdYlGn',
        cbar=False,
        linewidths=0.8,
        linecolor='#d1d5db',
        xticklabels=['Question', 'Student Feedback', 'Human Label', 'AI Label', 'Observation'],
        yticklabels=[str(i + 1) for i in range(rows)],
        ax=ax,
        vmin=0,
        vmax=1,
    )

    ax.set_title(
        'Comparison of AI and Human Emotion Classification',
        fontsize=16,
        fontweight='bold',
        pad=16,
    )
    ax.set_xlabel('')
    ax.set_ylabel('Sample #', fontsize=11)
    ax.tick_params(axis='x', labelsize=11, rotation=0)
    ax.tick_params(axis='y', labelsize=9, rotation=0)

    plt.tight_layout()
    fig.savefig(output_png, bbox_inches='tight')
    plt.close(fig)


def write_txt_table(df: pd.DataFrame, output_txt: Path) -> None:
    width_question = 24
    width_feedback = 70
    width_human = 14
    width_ai = 14
    width_observation = 96

    with output_txt.open('w', encoding='utf-8') as f:
        f.write('=' * 230 + '\n')
        f.write('Comparison of AI and Human Emotion Classification (All Mismatched Records)\n')
        f.write('=' * 230 + '\n\n')
        f.write(f'Total mismatched rows: {len(df)}\n\n')

        header = (
            f"{'Question':<{width_question}} | "
            f"{'Student Feedback':<{width_feedback}} | "
            f"{'Human Label':<{width_human}} | "
            f"{'AI Label':<{width_ai}} | "
            f"{'Observation':<{width_observation}}"
        )
        f.write(header + '\n')
        f.write('-' * 230 + '\n')

        for _, row in df.iterrows():
            question_lines = textwrap.wrap(str(row['question']), width_question) or ['']
            feedback_lines = textwrap.wrap(str(row['student_feedback']), width_feedback) or ['']
            human_lines = textwrap.wrap(str(row['human_label']), width_human) or ['']
            ai_lines = textwrap.wrap(str(row['ai_label']), width_ai) or ['']
            obs_lines = textwrap.wrap(str(row['observation']), width_observation) or ['']

            max_lines = max(len(question_lines), len(feedback_lines), len(human_lines), len(ai_lines), len(obs_lines))

            question_lines += [''] * (max_lines - len(question_lines))
            feedback_lines += [''] * (max_lines - len(feedback_lines))
            human_lines += [''] * (max_lines - len(human_lines))
            ai_lines += [''] * (max_lines - len(ai_lines))
            obs_lines += [''] * (max_lines - len(obs_lines))

            for i in range(max_lines):
                f.write(
                    f"{question_lines[i]:<{width_question}} | "
                    f"{feedback_lines[i]:<{width_feedback}} | "
                    f"{human_lines[i]:<{width_human}} | "
                    f"{ai_lines[i]:<{width_ai}} | "
                    f"{obs_lines[i]:<{width_observation}}\n"
                )
            f.write('-' * 230 + '\n')


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    ann_dir = base_dir / 'data' / 'annotations'
    out_dir = ann_dir / 'visualizations'
    out_dir.mkdir(parents=True, exist_ok=True)

    combined_file = ann_dir / 'combined_annotations_all.csv'
    master_file = ann_dir / 'Student Feedback Sentiment Annotation Form - Master Template.csv'
    cleaned_master_long_file = ann_dir / 'master_template_cleaned_long.csv'

    human_df = pd.read_csv(combined_file)
    human_df['feedback_id'] = human_df['feedback_id'].astype(str).str.strip().str.lower()
    human_df['human_label'] = human_df.apply(human_majority_label, axis=1)

    if cleaned_master_long_file.exists():
        ai_df = pd.read_csv(cleaned_master_long_file)
        ai_df['feedback_id'] = ai_df['feedback_id'].astype(str).str.strip().str.lower()
        ai_df['student_feedback'] = ai_df['student_feedback'].astype(str)
        ai_df['ai_label'] = ai_df['ai_label'].apply(normalize_label)
    else:
        ai_df = flatten_master_template(master_file)
    ai_df['feedback_id'] = ai_df['feedback_id'].astype(str).str.strip().str.lower()

    merged = human_df[['feedback_id', 'human_label']].merge(
        ai_df[['feedback_id', 'student_feedback', 'ai_label', 'question_num']],
        on='feedback_id',
        how='inner',
    )

    merged = merged[
        merged['human_label'].isin(VALID_EMOTIONS)
        & merged['ai_label'].isin(VALID_EMOTIONS)
    ].copy()

    # Filter empty and placeholder comments.
    merged['student_feedback_norm'] = merged['student_feedback'].apply(normalize_text)
    merged = merged[~merged['student_feedback_norm'].isin({'', 'n/a', 'none', 'null', 'nan'})].copy()

    merged['question'] = merged['question_num'].map(QUESTION_LABELS).fillna('Unknown Question')
    merged['observation'] = merged.apply(
        lambda r: build_observation(r['human_label'], r['ai_label'], r['student_feedback'], r['question']),
        axis=1,
    )

    # Keep only feedback entries where AI and human labels differ.
    sample = merged[merged['human_label'] != merged['ai_label']].copy()

    if sample.empty:
        raise RuntimeError('No comparable records found after filtering.')

    sample = sample[[
        'question',
        'student_feedback',
        'human_label',
        'ai_label',
        'observation',
    ]]

    # Keep all mismatches in tabular exports; cap visualization rows for readability.
    visual_sample = sample.head(20) if len(sample) > 20 else sample

    output_csv = out_dir / 'ai_human_comparison_table.csv'
    output_txt = out_dir / 'ai_human_comparison_table.txt'
    output_png = out_dir / 'seaborn_ai_human_comparison_table.png'

    sample.to_csv(output_csv, index=False, encoding='utf-8')
    write_txt_table(sample, output_txt)
    render_seaborn_table(visual_sample, output_png)

    print(f'Generated: {output_csv}')
    print(f'Generated: {output_txt}')
    print(f'Generated: {output_png}')
    print(f'Rows in full mismatch table: {len(sample)}')
    print(f'Rows shown in visualization: {len(visual_sample)}')


if __name__ == '__main__':
    main()
