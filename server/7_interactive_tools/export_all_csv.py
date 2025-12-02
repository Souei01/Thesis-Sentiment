"""
Export All CSV Files to Formatted Text Files
Creates txt files with grid table format for all CSV files
"""

import pandas as pd
import os
from pathlib import Path
from tabulate import tabulate

# Create output directory
output_dir = Path('csv_exports')
output_dir.mkdir(exist_ok=True)

# CSV files to export
csv_files = [
    'data/annotations/train_data.csv',
    'data/annotations/test_data.csv'
]

print('='*100)
print('EXPORTING CSV FILES TO TXT FORMAT')
print('='*100)

for csv_path in csv_files:
    if not os.path.exists(csv_path):
        print(f'\n⚠️  File not found: {csv_path}')
        continue
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Generate output filename
    csv_name = Path(csv_path).stem  # Get filename without extension
    output_file = output_dir / f'{csv_name}_full.txt'
    
    print(f'\n📄 Processing: {csv_path}')
    print(f'   Rows: {len(df)}, Columns: {len(df.columns)}')
    
    # Write to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('='*100 + '\n')
        f.write(f'{csv_name.upper().replace("_", " ")}\n')
        f.write('='*100 + '\n\n')
        f.write(f'Total samples: {len(df)}\n')
        f.write(f'Columns: {list(df.columns)}\n\n')
        
        # Write full dataframe using tabulate with grid format
        f.write(tabulate(df, headers='keys', tablefmt='grid', showindex=True))
        
        # Add emotion distribution if label column exists
        if 'label' in df.columns:
            f.write('\n\n' + '='*100 + '\n')
            f.write('Emotion Distribution:\n')
            emotion_dist = df['label'].value_counts().reset_index()
            emotion_dist.columns = ['Emotion', 'Count']
            f.write(tabulate(emotion_dist, headers='keys', tablefmt='grid', showindex=False))
        
        f.write('\n\n' + '='*100 + '\n')
    
    file_size = os.path.getsize(output_file) / 1024 / 1024  # Convert to MB
    print(f'   ✅ Exported to: {output_file}')
    print(f'   File size: {file_size:.2f} MB')

print('\n' + '='*100)
print('✅ ALL CSV FILES EXPORTED TO: csv_exports/')
print('='*100)
print('\nExported files:')
for txt_file in sorted(output_dir.glob('*.txt')):
    size = os.path.getsize(txt_file) / 1024 / 1024
    print(f'  - {txt_file.name} ({size:.2f} MB)')
