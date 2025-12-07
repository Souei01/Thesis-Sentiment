"""
Background task to run topic modeling and generate insights
Runs periodically using Celery or can be triggered manually
"""

import os
import django
import logging
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Feedback
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def should_run_topic_modeling():
    """
    Check if topic modeling should be run
    Run if:
    - New feedback added since last run
    - At least 10 feedbacks exist
    - Last run was more than 10 minutes ago
    """
    feedback_count = Feedback.objects.filter(status='submitted').count()
    
    # Need minimum feedbacks for meaningful topics
    if feedback_count < 10:
        logger.info(f"Only {feedback_count} feedbacks. Need at least 10 for topic modeling.")
        return False
    
    # Check last run time (from file timestamp)
    insights_file = Path('results/topic_modeling/lda_insights.json')
    if insights_file.exists():
        last_modified = datetime.fromtimestamp(insights_file.stat().st_mtime)
        minutes_since_last_run = (datetime.now() - last_modified).total_seconds() / 60
        
        if minutes_since_last_run < 10:  # Don't run if ran in last 10 minutes
            logger.info(f"Topic modeling ran {minutes_since_last_run:.1f} minutes ago. Skipping.")
            return False
    
    return True


def run_topic_modeling_task():
    """
    Run LDA topic modeling and generate GPT-Neo insights
    This is the background task that can be called automatically
    """
    logger.info("Starting background topic modeling task...")
    
    if not should_run_topic_modeling():
        return {"status": "skipped", "reason": "Conditions not met"}
    
    try:
        # Import here to avoid circular imports
        import subprocess
        import sys
        
        # Get Python executable from virtual environment
        python_exe = sys.executable
        script_path = Path(__file__).parent / 'run_lda_from_db.py'  # Use database script
        
        logger.info(f"Running LDA script: {script_path}")
        
        # Run the LDA script
        result = subprocess.run(
            [python_exe, str(script_path)],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Topic modeling completed successfully")
            return {
                "status": "success",
                "message": "Topic modeling and insights generated",
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Topic modeling failed: {result.stderr}")
            return {
                "status": "error",
                "message": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error running topic modeling task: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == '__main__':
    print('='*100)
    print('BACKGROUND TOPIC MODELING TASK')
    print('='*100)
    result = run_topic_modeling_task()
    print(f"\nResult: {result}")
