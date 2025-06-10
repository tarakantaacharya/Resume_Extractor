"""
Setup script to automate the entire Resume Extractor pipeline
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n🔧 Installing dependencies...")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("⚠️  Warning: spaCy model download failed. You may need to download it manually.")
    
    return True

def generate_data():
    """Generate sample resume data"""
    return run_command("python data/generate_sample_resumes.py", "Generating sample resume data")

def create_annotations():
    """Create training annotations"""
    return run_command("python annotations/create_annotations.py", "Creating training annotations")

def train_model():
    """Train the NER model"""
    return run_command("python train_ner.py", "Training NER model (this may take 5-10 minutes)")

def test_inference():
    """Test the inference pipeline"""
    return run_command("python inference.py", "Testing inference pipeline")

def main():
    """Main setup function"""
    print("🚀 Resume Skill Extractor Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check the error messages above.")
        sys.exit(1)
    
    # Generate sample data
    if not generate_data():
        print("❌ Failed to generate sample data.")
        sys.exit(1)
    
    # Create annotations
    if not create_annotations():
        print("❌ Failed to create annotations.")
        sys.exit(1)
    
    # Train model
    if not train_model():
        print("❌ Failed to train model.")
        sys.exit(1)
    
    # Test inference
    if not test_inference():
        print("❌ Failed to test inference.")
        sys.exit(1)
    
    # Success message
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("""
✅ All components have been set up successfully!

🚀 Next Steps:
1. Run the Streamlit app: streamlit run app.py
2. Or run the Gradio app: python gradio_app.py
3. Upload a resume file or paste resume text to test

📁 Generated Files:
- Sample resumes: data/sample_resumes/
- Training data: annotations/training_data.json
- Trained model: models/resume_ner_model/
- Training curve: models/training_curve.png

📚 Documentation:
- Read README.md for detailed usage instructions
- Check the web interface for interactive testing

Happy resume extracting! 🎯
""")

if __name__ == "__main__":
    main()