# Fleiss Kappa Data

This folder contains CSV files for Fleiss Kappa inter-rater reliability analysis of student feedback emotion classification.

## Purpose
Fleiss Kappa is used to measure the agreement between multiple annotators/raters when categorizing feedback emotions.

## File Format
CSV files should contain:
- **Rows**: Feedback items/responses
- **Columns**: Ratings from 3 annotators

### Example CSV Structure:
```csv
feedback_id,annotator_1,annotator_2,annotator_3
1,joy,joy,satisfaction
2,disappointment,disappointment,disappointment
3,acceptance,acceptance,acceptance
4,boredom,boredom,acceptance
5,satisfaction,satisfaction,joy
```

## Emotion Categories (5 emotions):
1. **joy** - Positive, happy emotions (very positive)
2. **satisfaction** - Content, pleased emotions (positive)
3. **acceptance** - Neutral, accepting emotions (neutral)
4. **boredom** - Disinterested, unengaged emotions (slightly negative)
5. **disappointment** - Negative, dissatisfied emotions (negative)

## How to Use:
1. Place your annotated CSV files in this folder
2. Ensure you have 3 annotators' columns in your CSV
3. Run the Fleiss Kappa calculation script:
   ```bash
   python calculate_fleiss_kappa.py data/fleiss_kappa/your_file.csv
   ```
4. Results will show:
   - Fleiss Kappa coefficient (0-1)
   - Inter-rater agreement interpretation
   - Emotion category distribution
   - Pairwise agreement matrix
   - Disagreement cases

## Kappa Interpretation:
- **< 0.00**: Poor agreement (worse than chance)
- **0.00-0.20**: Slight agreement
- **0.21-0.40**: Fair agreement
- **0.41-0.60**: Moderate agreement
- **0.61-0.80**: Substantial agreement
- **0.81-1.00**: Almost perfect agreement

## Files:
- `sample_annotations.csv` - Example template with 5 emotions
- Place your annotation files here (e.g., `Student Feedback Sentiment Annotation Form - Annotator-1.csv`)

