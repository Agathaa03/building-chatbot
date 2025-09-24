#!/usr/bin/env python3
"""
Automation Script for Summer Practice Project
Handles file processing, chatbot training, and deployment automation
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import argparse
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ProjectAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from config.json"""
        config_path = self.project_root / 'config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            "training_data_path": "data/training_data.json",
            "model_save_path": "models/",
            "test_files": ["test_chatbot.py", "test_api.py"],
            "deploy_commands": ["npm run build", "git add .", "git commit -m 'auto-deploy'", "git push"]
        }
    
    def setup_project_structure(self):
        """Create necessary directories and files"""
        directories = [
            'data',
            'models', 
            'src',
            'tests',
            'docs',
            'scripts',
            'logs'
        ]
        
        files = {
            'data/training_data.json': '{"intents": []}',
            'src/__init__.py': '',
            'tests/__init__.py': '',
            'requirements.txt': self.generate_requirements()
        }
        
        logging.info("Setting up project structure...")
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            logging.info(f"Created directory: {directory}")
        
        for file_path, content in files.items():
            file_full_path = self.project_root / file_path
            if not file_full_path.exists():
                with open(file_full_path, 'w') as f:
                    f.write(content)
                logging.info(f"Created file: {file_path}")
    
    def generate_requirements(self):
        """Generate requirements.txt content"""
        return """\
flask>=2.3.0
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
nltk>=3.6.0
requests>=2.25.0
python-dotenv>=0.19.0
gunicorn>=20.1.0
pytest>=6.2.0
"""
    
    def run_tests(self):
        """Run all automated tests"""
        logging.info("Running tests...")
        
        test_scripts = [
            "python -m pytest tests/ -v",
            "python -c \"import src.chatbot; print('Chatbot module imports successfully')\"",
            "python -c \"import src.api; print('API module imports successfully')\""
        ]
        
        for test_cmd in test_scripts:
            try:
                result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    logging.info(f"✓ Test passed: {test_cmd}")
                else:
                    logging.error(f"✗ Test failed: {test_cmd}")
                    logging.error(result.stderr)
            except Exception as e:
                logging.error(f"Error running test {test_cmd}: {e}")
    
    def train_chatbot_model(self):
        """Automate chatbot model training"""
        logging.info("Training chatbot model...")
        
        try:
            # Import and train model
            training_script = """
import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib
import numpy as np

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

class ChatbotTrainer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = LinearSVC()
        
    def load_data(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def train(self, data_path):
        data = self.load_data(data_path)
        
        texts = []
        labels = []
        
        for intent in data['intents']:
            for pattern in intent['patterns']:
                texts.append(pattern)
                labels.append(intent['tag'])
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)
        
        # Train classifier
        self.classifier.fit(X, y)
        
        # Save model
        joblib.dump({
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'classes': self.classifier.classes_
        }, 'models/chatbot_model.pkl')
        
        print(f"Model trained on {len(texts)} samples")
        return len(texts)

if __name__ == "__main__":
    trainer = ChatbotTrainer()
    sample_count = trainer.train('data/training_data.json')
            """
            
            with open('train_model.py', 'w') as f:
                f.write(training_script)
            
            result = subprocess.run([sys.executable, 'train_model.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("✓ Chatbot model trained successfully")
                logging.info(result.stdout)
            else:
                logging.error("✗ Model training failed")
                logging.error(result.stderr)
                
            # Cleanup temporary file
            if os.path.exists('train_model.py'):
                os.remove('train_model.py')
                
        except Exception as e:
            logging.error(f"Error training model: {e}")
    
    def backup_project(self):
        """Create project backup"""
        logging.info("Creating project backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / 'backups' / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy important files
        important_files = [
            'src/', 'data/', 'models/', 'tests/',
            'requirements.txt', 'config.json', 'auto.py'
        ]
        
        try:
            import shutil
            for item in important_files:
                source = self.project_root / item
                if source.exists():
                    if source.is_dir():
                        shutil.copytree(source, backup_dir / item)
                    else:
                        shutil.copy2(source, backup_dir / item)
            
            logging.info(f"✓ Backup created: {backup_dir}")
        except Exception as e:
            logging.error(f"Backup failed: {e}")
    
    def deploy_project(self):
        """Automate deployment steps"""
        logging.info("Starting deployment...")
        
        deploy_commands = self.config.get('deploy_commands', [])
        
        for cmd in deploy_commands:
            try:
                logging.info(f"Running: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    logging.info(f"✓ Command successful: {cmd}")
                else:
                    logging.error(f"✗ Command failed: {cmd}")
                    logging.error(result.stderr)
            except Exception as e:
                logging.error(f"Error running command {cmd}: {e}")
    
    def generate_docs(self):
        """Generate project documentation"""
        logging.info("Generating documentation...")
        
        docs_content = f"""
# Summer Practice Project Documentation

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Project Structure
