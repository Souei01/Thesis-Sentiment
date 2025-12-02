"""
Download Pre-trained Models Without PyTorch
Uses HuggingFace Hub API to download model files
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def download_with_hub():
    """Download models using HuggingFace Hub"""
    try:
        from huggingface_hub import snapshot_download
        
        print("=" * 80)
        print("DOWNLOADING PRE-TRAINED MODELS")
        print("Using HuggingFace Hub (No PyTorch required)")
        print("=" * 80)
        print()
        
        models = [
            {
                'repo': 'roberta-base',
                'local_dir': 'ml_models/roberta',
                'name': 'RoBERTa',
                'description': '⭐ RECOMMENDED for sentiment analysis'
            },
            {
                'repo': 'bert-base-multilingual-cased',
                'local_dir': 'ml_models/mbert',
                'name': 'mBERT',
                'description': 'Multilingual BERT (104 languages)'
            },
            {
                'repo': 'distilbert-base-uncased',
                'local_dir': 'ml_models/distilbert',
                'name': 'DistilBERT',
                'description': 'Faster, lighter alternative'
            }
        ]
        
        print("📋 Models to download:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model['name']} - {model['description']}")
        print()
        print("⚠️  Total download size: ~1.5GB")
        print("⚠️  This may take 10-30 minutes depending on internet speed")
        print()
        
        proceed = input("Continue with download? (y/n) [y]: ").strip().lower() or 'y'
        
        if proceed != 'y':
            print("Download cancelled.")
            return
        
        for model in models:
            print("\n" + "=" * 80)
            print(f"📥 Downloading: {model['name']}")
            print(f"   Repository: {model['repo']}")
            print(f"   Description: {model['description']}")
            print("=" * 80)
            
            try:
                local_path = Path(model['local_dir'])
                local_path.mkdir(parents=True, exist_ok=True)
                
                print(f"\n⏳ Downloading to: {local_path.absolute()}")
                print("   This may take several minutes...")
                
                # Download all files from the model repository
                snapshot_download(
                    repo_id=model['repo'],
                    local_dir=str(local_path),
                    local_dir_use_symlinks=False
                )
                
                print(f"✅ Successfully downloaded: {model['name']}")
                
                # List downloaded files
                files = list(local_path.glob('*'))
                print(f"\n📁 Downloaded {len(files)} files:")
                for file in files[:10]:
                    size = file.stat().st_size / (1024 * 1024)  # MB
                    print(f"   - {file.name} ({size:.1f} MB)")
                if len(files) > 10:
                    print(f"   ... and {len(files) - 10} more files")
                    
            except Exception as e:
                print(f"❌ Error downloading {model['name']}: {e}")
                continue
        
        print("\n" + "=" * 80)
        print("✅ DOWNLOAD COMPLETE!")
        print("=" * 80)
        print("\n📁 Models saved to:")
        print("   - ml_models/roberta/ (RoBERTa)")
        print("   - ml_models/mbert/ (mBERT)")
        print("   - ml_models/distilbert/ (DistilBERT)")
        print()
        print("🎯 Next steps:")
        print("   1. Models are ready for fine-tuning")
        print("   2. Use RoBERTa for best sentiment analysis results")
        print("   3. Training data: data/annotations/training_data_balanced.csv")
        print()
        print("⚠️  Note: For model training, you'll need PyTorch")
        print("   PyTorch requires Python 3.11 or 3.12 (not 3.14)")
        print("=" * 80)
        
    except ImportError:
        print("❌ Error: huggingface_hub not found")
        print("\nInstall with:")
        print("   pip install huggingface_hub")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    download_with_hub()
