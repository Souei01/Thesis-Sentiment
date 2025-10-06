from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
import os

def load_training_data(request):
    # Path to your training data file
    data_path = os.path.join('server', 'data', 'Data Sample Training.xlsx - Annotator 1.csv')
    try:
        df = pd.read_csv(data_path)
        
        # Create separate rows for each feedback type with its corresponding label
        rows = []
        
        for index, row in df.iterrows():
            # Add suggested_changes row (include even if empty)
            feedback_text = row['suggested_changes'] if pd.notna(row['suggested_changes']) else 'No response'
            rows.append({
                'question': 'suggested_changes',
                'feedback': feedback_text,
                'label': row['suggested_changes_label'],
            })
            
            # Add best_teaching_aspect row (include even if empty)
            feedback_text = row['best_teaching_aspect'] if pd.notna(row['best_teaching_aspect']) else 'No response'
            rows.append({
                'question': 'best_teaching_aspect',
                'feedback': feedback_text,
                'label': row['best_teaching_aspect_label'],
            })
            
            # Add least_teaching_aspect row (include even if empty)
            feedback_text = row['least_teaching_aspect'] if pd.notna(row['least_teaching_aspect']) else 'No response'
            rows.append({
                'question': 'least_teaching_aspect',
                'feedback': feedback_text,
                'label': row['least_teaching_aspect_label'],
            })
            
            # Add further_comments row (include even if empty)
            feedback_text = row['further_comments'] if pd.notna(row['further_comments']) else 'No response'
            rows.append({
                'question': 'further_comments',
                'feedback': feedback_text,
                'label': row['further_comments_label'],
            })
        
        # Create new DataFrame with separate rows
        training_df = pd.DataFrame(rows)
        
        print(training_df.head())  # Show first 5 rows in terminal
        print(training_df.info())    # Show column info and data types
        
        # Convert ALL DataFrame rows to HTML table for browser viewing
        html_table = training_df.to_html(classes='table table-striped', table_id='data-preview')
        
        html_content = f"""
        <html>
        <head>
            <title>Data Preview</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .info {{ background-color: #f0f0f0; padding: 10px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="info">
                <p><strong>Shape:</strong> {training_df.shape[0]} rows, {training_df.shape[1]} columns</p>
                <p><strong>Columns:</strong> {', '.join(training_df.columns)}</p>
            </div>
            {html_table}
        </body>
        </html>
        """
        
        return HttpResponse(html_content)
    except Exception as e:
        return JsonResponse({'error': str(e)})