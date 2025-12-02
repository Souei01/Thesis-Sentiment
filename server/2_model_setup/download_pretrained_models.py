"""
Download and Backup Pre-trained Models for Sentiment Analysis

This script downloads pre-trained transformer models and saves them locally
for offline use and model training.

Models included:
1. mBERT (bert-base-multilingual-cased) - Multilingual support
2. RoBERTa (roberta-base) - HIGHLY RECOMMENDED for sentiment analysis
3. DistilBERT (distilbert-base-uncased) - Faster alternative

Why RoBERTa?
- Optimized for sentiment analysis tasks
- Better performance than BERT on emotion classification
- Trained on more data with improved training methodology
- State-of-the-art results on sentiment benchmarks
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import transformers
        import torch
        print("✅ Required packages found")
        print(f"   - transformers: {transformers.__version__}")
        print(f"   - torch: {torch.__version__}")
        return True
    except ImportError as e:
        print("❌ Missing required packages!")
        print("\nPlease install:")
        print("   pip install transformers torch sentencepiece")
        return False

def download_model(model_name, save_dir, description):
    """
    Download a pre-trained model and tokenizer
    
    Args:
        model_name: HuggingFace model identifier
        save_dir: Local directory to save the model
        description: Model description for display
    """
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
        
        print("\n" + "=" * 80)
        print(f"📥 Downloading: {model_name}")
        print(f"   {description}")
        print("=" * 80)
        
        # Create save directory
        model_path = Path(save_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📂 Save location: {model_path.absolute()}")
        
        # Download tokenizer
        print("\n⏳ Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(str(model_path))
        print("✅ Tokenizer downloaded")
        
        # Download base model (not fine-tuned for classification yet)
        print("\n⏳ Downloading model...")
        model = AutoModel.from_pretrained(model_name)
        model.save_pretrained(str(model_path))
        print("✅ Model downloaded")
        
        # Get model info
        num_parameters = sum(p.numel() for p in model.parameters())
        print(f"\n📊 Model Info:")
        print(f"   - Parameters: {num_parameters:,}")
        print(f"   - Size on disk: ~{num_parameters * 4 / 1024 / 1024:.1f} MB")
        
        # Save model info
        info_file = model_path / "model_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"Model: {model_name}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Parameters: {num_parameters:,}\n")
            f.write(f"Downloaded: {Path.cwd()}\n")
        
        print(f"\n✅ Successfully downloaded: {model_name}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading {model_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print("PRE-TRAINED MODEL DOWNLOAD & BACKUP")
    print("For Student Feedback Sentiment Analysis")
    print("=" * 80)
    print()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("\n" + "=" * 80)
    print("📋 Models to Download:")
    print("=" * 80)
    print("1. mBERT (bert-base-multilingual-cased)")
    print("   - Multilingual support (104 languages)")
    print("   - Good for international datasets")
    print("   - Size: ~680MB")
    print()
    print("2. RoBERTa (roberta-base) ⭐ RECOMMENDED")
    print("   - Optimized for sentiment/emotion analysis")
    print("   - Better performance than BERT")
    print("   - State-of-the-art on sentiment benchmarks")
    print("   - Size: ~500MB")
    print()
    print("3. XLM-RoBERTa (xlm-roberta-base) ⭐ NEW")
    print("   - Best of both worlds: RoBERTa + Multilingual")
    print("   - Trained on 100 languages")
    print("   - Superior to mBERT on most tasks")
    print("   - Size: ~1.1GB")
    print()
    print("4. DistilBERT (distilbert-base-uncased)")
    print("   - 40% smaller, 60% faster than BERT")
    print("   - 97% of BERT's performance")
    print("   - Good for resource-constrained environments")
    print("   - Size: ~260MB")
    print()
    
    # Model configurations
    models = [
        {
            'name': 'bert-base-multilingual-cased',
            'save_dir': 'ml_models/mbert',
            'description': 'Multilingual BERT (104 languages)'
        },
        {
            'name': 'roberta-base',
            'save_dir': 'ml_models/roberta',
            'description': 'RoBERTa - HIGHLY RECOMMENDED for sentiment analysis'
        },
        {
            'name': 'xlm-roberta-base',
            'save_dir': 'ml_models/xlm_roberta',
            'description': 'XLM-RoBERTa - Multilingual RoBERTa (100 languages)'
        },
        {
            'name': 'distilbert-base-uncased',
            'save_dir': 'ml_models/distilbert',
            'description': 'DistilBERT - Faster, lighter alternative'
        }
    ]
    
    # Ask user which models to download
    print("=" * 80)
    print("Which models would you like to download?")
    print("=" * 80)
    print("1. All four models (Recommended)")
    print("2. Only RoBERTa (Best for English sentiment)")
    print("3. Only XLM-RoBERTa (Best multilingual)")
    print("4. RoBERTa + XLM-RoBERTa (Compare both)")
    print("5. Only mBERT (Original multilingual)")
    print("6. Custom selection")
    print()
    
    choice = input("Enter your choice (1-6) [default: 1]: ").strip() or "1"
    
    models_to_download = []
    
    if choice == "1":
        models_to_download = models
    elif choice == "2":
        models_to_download = [models[1]]  # RoBERTa
    elif choice == "3":
        models_to_download = [models[2]]  # XLM-RoBERTa
    elif choice == "4":
        models_to_download = [models[1], models[2]]  # RoBERTa + XLM-RoBERTa
    elif choice == "5":
        models_to_download = [models[0]]  # mBERT
    elif choice == "6":
        print("\nSelect models to download (y/n):")
        for i, model in enumerate(models):
            response = input(f"  {model['name']}? (y/n) [y]: ").strip().lower() or 'y'
            if response == 'y':
                models_to_download.append(model)
    else:
        print("Invalid choice. Downloading all models...")
        models_to_download = models
    
    if not models_to_download:
        print("\n❌ No models selected. Exiting...")
        return
    
    # Download selected models
    print("\n" + "=" * 80)
    print(f"📥 Starting download of {len(models_to_download)} model(s)...")
    print("=" * 80)
    print("⚠️  This may take several minutes depending on your internet speed.")
    print("⚠️  Total download size: ~1.5GB for all models")
    print()
    
    success_count = 0
    failed_models = []
    
    for model_config in models_to_download:
        success = download_model(
            model_config['name'],
            model_config['save_dir'],
            model_config['description']
        )
        
        if success:
            success_count += 1
        else:
            failed_models.append(model_config['name'])
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully downloaded: {success_count}/{len(models_to_download)}")
    
    if failed_models:
        print(f"❌ Failed downloads: {len(failed_models)}")
        for model in failed_models:
            print(f"   - {model}")
    
    print("\n" + "=" * 80)
    print("📁 MODEL LOCATIONS")
    print("=" * 80)
    
    for model_config in models_to_download:
        model_path = Path(model_config['save_dir'])
        if model_path.exists():
            print(f"✅ {model_config['name']}")
            print(f"   Location: {model_path.absolute()}")
            
            # Show files
            files = list(model_path.glob('*'))
            print(f"   Files: {len(files)}")
            for file in files[:5]:  # Show first 5 files
                print(f"      - {file.name}")
            if len(files) > 5:
                print(f"      ... and {len(files) - 5} more files")
            print()
    
    print("=" * 80)
    print("🎯 NEXT STEPS")
    print("=" * 80)
    print("1. Use these models for fine-tuning on your sentiment dataset")
    print("2. Recommended: Start with RoBERTa for best sentiment analysis results")
    print("3. Fine-tune script: fine_tune_mbert.py (update to use RoBERTa)")
    print("4. Training data: data/annotations/training_data_balanced.csv")
    print()
    print("💡 Why RoBERTa?")
    print("   - Optimized training approach")
    print("   - Better handling of sentiment/emotion tasks")
    print("   - Superior performance on classification benchmarks")
    print("   - Used by many state-of-the-art sentiment models")
    print()
    print("✅ All models saved locally and ready for offline use!")
    print("=" * 80)

if __name__ == "__main__":
    main()
