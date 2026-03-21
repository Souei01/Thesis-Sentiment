from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import cohen_kappa_score


def normalize_label(value: str) -> str:
    v = str(value).strip().lower()
    if v in ['', 'nan', 'none', 'null', 'n/a']:
        return 'null'
    return v


def extract_text_label_pairs(df: pd.DataFrame):
    cols = list(df.columns)
    pairs = []
    for i, col in enumerate(cols):
        if str(col).strip().lower().startswith('label'):
            continue
        nxt = cols[i + 1] if i + 1 < len(cols) else None
        if nxt and str(nxt).strip().lower().startswith('label'):
            pairs.append((col, nxt))
    return pairs


def flatten(path: Path, key: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    pairs = extract_text_label_pairs(raw)
    rows = []
    for ridx, row in raw.iterrows():
        respondent_id = ridx + 1
        for qidx, (_, label_col) in enumerate(pairs, start=1):
            rows.append(
                {
                    'respondent_id': respondent_id,
                    'question_num': qidx,
                    key: normalize_label(row.get(label_col, 'null')),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    ann_dir = base_dir / 'data' / 'annotations'
    out_dir = ann_dir / 'visualizations'
    out_dir.mkdir(parents=True, exist_ok=True)

    a1 = flatten(ann_dir / 'Student Feedback Sentiment Annotation Form - Annotator-1.csv', 'annotator_1')
    a2 = flatten(ann_dir / 'Student Feedback Sentiment Annotation Form - Annotator-2.csv', 'annotator_2')
    a3 = flatten(ann_dir / 'Student Feedback Sentiment Annotation Form - Annotator-3.csv', 'annotator_3')
    ai = flatten(ann_dir / 'Student Feedback Sentiment Annotation Form - Master Template.csv', 'ai')

    merged = a1.merge(a2, on=['respondent_id', 'question_num']) \
               .merge(a3, on=['respondent_id', 'question_num']) \
               .merge(ai, on=['respondent_id', 'question_num'])

    valid = {'joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment'}
    comp = merged[
        merged['annotator_1'].isin(valid)
        & merged['annotator_2'].isin(valid)
        & merged['annotator_3'].isin(valid)
        & merged['ai'].isin(valid)
    ].copy()

    sources = ['annotator_1', 'annotator_2', 'annotator_3', 'ai']

    # Pairwise agreement (% exact match)
    agreement = pd.DataFrame(index=sources, columns=sources, dtype=float)
    kappa = pd.DataFrame(index=sources, columns=sources, dtype=float)

    for s1 in sources:
        for s2 in sources:
            agreement.loc[s1, s2] = (comp[s1] == comp[s2]).mean() * 100
            kappa.loc[s1, s2] = cohen_kappa_score(comp[s1], comp[s2])

    # Label distribution by source
    dist_rows = []
    for src in sources:
        counts = comp[src].value_counts(normalize=True)
        for emo in sorted(valid):
            dist_rows.append(
                {
                    'source': src,
                    'emotion': emo,
                    'percentage': counts.get(emo, 0) * 100,
                }
            )
    dist = pd.DataFrame(dist_rows)

    display_names = {
        'annotator_1': 'Annotator 1',
        'annotator_2': 'Annotator 2',
        'annotator_3': 'Annotator 3',
        'ai': 'AI (Master Template)',
    }
    agreement = agreement.rename(index=display_names, columns=display_names)
    kappa = kappa.rename(index=display_names, columns=display_names)
    dist['source'] = dist['source'].map(display_names)

    sns.set_theme(style='whitegrid', context='talk')

    # 1) Exact agreement heatmap
    fig1, ax1 = plt.subplots(figsize=(8, 7), dpi=150)
    sns.heatmap(
        agreement,
        annot=True,
        fmt='.1f',
        cmap='YlGnBu',
        cbar_kws={'label': 'Exact Agreement (%)'},
        ax=ax1,
        vmin=0,
        vmax=100,
    )
    ax1.set_title(f'Pairwise Exact Agreement (%)\n(n={len(comp)} comparable annotations)', fontweight='bold')
    fig1.tight_layout()
    out_file1 = out_dir / 'seaborn_exact_agreement_heatmap.png'
    fig1.savefig(out_file1, bbox_inches='tight')
    plt.close(fig1)
    print(f'Generated: {out_file1}')

    # 2) Fleiss' Kappa heatmap (labeling per request)
    fig2, ax2 = plt.subplots(figsize=(8, 7), dpi=150)
    sns.heatmap(
        kappa,
        annot=True,
        fmt='.3f',
        cmap='PuBuGn',
        cbar_kws={'label': "Fleiss' Kappa"},
        ax=ax2,
        vmin=0,
        vmax=1,
    )
    ax2.set_title(f"Pairwise Fleiss' Kappa\n(n={len(comp)} comparable annotations)", fontweight='bold')
    fig2.tight_layout()
    out_file2 = out_dir / 'seaborn_fleiss_kappa_heatmap.png'
    fig2.savefig(out_file2, bbox_inches='tight')
    plt.close(fig2)
    print(f'Generated: {out_file2}')

    # 3) Emotion distribution by source
    fig3, ax3 = plt.subplots(figsize=(11, 7), dpi=150)
    sns.barplot(
        data=dist,
        x='emotion',
        y='percentage',
        hue='source',
        ax=ax3,
        palette='Set2',
    )
    ax3.set_title(f'Emotion Distribution by Source\n(n={len(comp)} comparable annotations)', fontweight='bold')
    ax3.set_xlabel('Emotion')
    ax3.set_ylabel('Percentage (%)')
    ax3.tick_params(axis='x', rotation=25)
    ax3.legend(title='Source', fontsize=10, title_fontsize=11)
    fig3.tight_layout()
    out_file3 = out_dir / 'seaborn_emotion_distribution_by_source.png'
    fig3.savefig(out_file3, bbox_inches='tight')
    plt.close(fig3)
    print(f'Generated: {out_file3}')


if __name__ == '__main__':
    main()
