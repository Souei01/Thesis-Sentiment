import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    annotations_dir = base_dir / 'data' / 'annotations'
    input_csv = annotations_dir / 'combined_annotations_all.csv'
    output_dir = annotations_dir / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_bar_png = output_dir / 'seaborn_question_emotion_count_bar.png'
    output_heatmap_png = output_dir / 'seaborn_question_emotion_percentage_heatmap.png'

    if not input_csv.exists():
        raise FileNotFoundError(f'Missing input file: {input_csv}')

    df = pd.read_csv(input_csv)

    required = {'feedback_id', 'annotator_1', 'annotator_2', 'annotator_3'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')

    # Majority-vote expert label from 3 annotators
    df['expert_label'] = df[['annotator_1', 'annotator_2', 'annotator_3']].mode(axis=1)[0].astype(str).str.strip().str.lower()

    # Extract question number from feedback_id pattern like q1_f123
    pattern = re.compile(r'^q([1-4])_f\d+$', re.IGNORECASE)

    def extract_question_num(feedback_id: str):
        match = pattern.match(str(feedback_id).strip())
        return int(match.group(1)) if match else None

    df['question_num'] = df['feedback_id'].apply(extract_question_num)
    df = df[df['question_num'].notna()].copy()
    df['question_num'] = df['question_num'].astype(int)

    valid_emotions = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment']
    df = df[df['expert_label'].isin(valid_emotions)].copy()

    question_labels = {
        1: 'Q1: Course Improvement',
        2: 'Q2: Best Teaching',
        3: 'Q3: Least Teaching',
        4: 'Q4: Constructive Comment',
    }

    count_df = (
        df.groupby(['question_num', 'expert_label'])
        .size()
        .reset_index(name='count')
    )
    count_df['question_label'] = count_df['question_num'].map(question_labels)

    # Percentage per question for easier interpretation in thesis
    total_per_question = count_df.groupby('question_label')['count'].transform('sum')
    count_df['percentage'] = (count_df['count'] / total_per_question) * 100

    sns.set_theme(style='whitegrid', context='talk')

    # Plot 1: grouped bar (count)
    fig1, ax1 = plt.subplots(figsize=(11, 7), dpi=150)
    sns.barplot(
        data=count_df,
        x='question_label',
        y='count',
        hue='expert_label',
        hue_order=valid_emotions,
        palette='Set2',
        ax=ax1,
    )
    ax1.set_title('Emotion Count by Question (Majority Expert Label)', pad=12, fontweight='bold')
    ax1.set_xlabel('Question')
    ax1.set_ylabel('Count')
    ax1.tick_params(axis='x', rotation=20)
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, title='Emotion', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    fig1.tight_layout()
    fig1.savefig(output_bar_png, bbox_inches='tight')
    plt.close(fig1)

    # Plot 2: heatmap (percentage)
    fig2, ax2 = plt.subplots(figsize=(10, 7), dpi=150)
    heatmap_df = count_df.pivot(index='expert_label', columns='question_label', values='percentage').reindex(valid_emotions)
    sns.heatmap(
        heatmap_df,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Percentage (%)'},
        ax=ax2,
    )
    ax2.set_title('Emotion Percentage Heatmap by Question', pad=12, fontweight='bold')
    ax2.set_xlabel('Question')
    ax2.set_ylabel('Emotion')
    fig2.tight_layout()
    fig2.savefig(output_heatmap_png, bbox_inches='tight')
    plt.close(fig2)

    print(f'Generated: {output_bar_png}')
    print(f'Generated: {output_heatmap_png}')


if __name__ == '__main__':
    main()
