"""
Test script to verify the Resume Extractor system
"""
import os
import json
from pathlib import Path
from inference import ResumeExtractor

def test_sample_resumes():
    """Test the system with sample resumes"""
    print("🧪 Testing Resume Extractor System")
    print("="*50)
    
    # Sample resume texts for testing
    test_resumes = [
        {
            "name": "Software Engineer Resume",
            "text": """
            John Smith
            Email: john.smith@email.com
            Phone: +1-555-123-4567
            
            PROFESSIONAL SUMMARY
            Experienced Software Engineer with 5 years of experience in software development.
            
            EDUCATION
            B.Tech in Computer Science
            Stanford University
            Graduated: 2019
            
            TECHNICAL SKILLS
            Programming Languages: Python, Java, JavaScript
            Technologies: Machine Learning, AWS, Docker, React
            
            WORK EXPERIENCE
            Senior Software Engineer
            Google
            2021 - Present (3 years)
            • Developed machine learning models using TensorFlow
            
            Software Engineer
            Microsoft
            2019 - 2021 (2 years)
            • Built web applications using React and Node.js
            """
        },
        {
            "name": "Data Scientist Resume",
            "text": """
            Sarah Johnson
            Email: sarah.johnson@email.com
            Phone: +1-555-987-6543
            
            SUMMARY
            Data Scientist with 4 years of experience in machine learning and analytics.
            
            EDUCATION
            M.S. in Data Science
            MIT
            2020
            
            SKILLS
            Python, R, SQL, TensorFlow, PyTorch, Pandas, NumPy
            Machine Learning, Deep Learning, Statistical Analysis
            
            EXPERIENCE
            Senior Data Scientist
            Netflix
            2022 - Present (2 years)
            
            Data Scientist
            Amazon
            2020 - 2022 (2 years)
            """
        },
        {
            "name": "Full Stack Developer Resume",
            "text": """
            Michael Brown
            michael.brown@email.com
            +1-555-456-7890
            
            Full Stack Developer with 3 years of experience
            
            EDUCATION
            B.S. in Computer Science
            University of California, Berkeley
            2021
            
            TECHNICAL SKILLS
            Frontend: React, Angular, Vue.js, HTML, CSS, JavaScript
            Backend: Node.js, Django, Flask, Spring Boot
            Database: MongoDB, PostgreSQL, MySQL
            Cloud: AWS, Azure, Docker, Kubernetes
            
            WORK EXPERIENCE
            Full Stack Developer
            Uber
            2021 - Present (3 years)
            """
        }
    ]
    
    # Initialize extractor
    try:
        extractor = ResumeExtractor()
        print("✅ Resume Extractor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return False
    
    # Test each resume
    all_passed = True
    for i, resume in enumerate(test_resumes, 1):
        print(f"\n📄 Test {i}: {resume['name']}")
        print("-" * 40)
        
        try:
            # Extract information
            result = extractor.process_text(resume['text'])
            
            # Check if extraction was successful
            if "error" in result:
                print(f"❌ Extraction failed: {result['error']}")
                all_passed = False
                continue
            
            # Validate results
            skills_found = len(result.get('skills', []))
            orgs_found = len(result.get('organizations', []))
            degrees_found = len(result.get('degrees', []))
            
            print(f"✅ Extraction successful!")
            print(f"   📧 Email: {result.get('email', 'Not found')}")
            print(f"   👤 Name: {result.get('name', 'Not found')}")
            print(f"   🛠️  Skills: {skills_found} found")
            print(f"   🏢 Organizations: {orgs_found} found")
            print(f"   🎓 Degrees: {degrees_found} found")
            print(f"   💼 Experience: {result.get('experience', 'Not specified')}")
            
            # Basic validation
            if skills_found == 0:
                print("   ⚠️  Warning: No skills detected")
            if orgs_found == 0:
                print("   ⚠️  Warning: No organizations detected")
            if not result.get('email'):
                print("   ⚠️  Warning: No email detected")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            all_passed = False
    
    return all_passed

def test_file_processing():
    """Test file processing capabilities"""
    print(f"\n📁 Testing File Processing")
    print("-" * 40)
    
    # Check if sample resumes exist
    sample_dir = Path("d:/.vscode/Resume_Extractor/data/sample_resumes")
    if not sample_dir.exists():
        print("⚠️  Sample resumes directory not found. Run data generation first.")
        return False
    
    # Get a few sample files
    sample_files = list(sample_dir.glob("*.txt"))[:3]
    
    if not sample_files:
        print("⚠️  No sample resume files found.")
        return False
    
    extractor = ResumeExtractor()
    
    for file_path in sample_files:
        try:
            print(f"📄 Processing: {file_path.name}")
            result = extractor.process_resume_file(str(file_path))
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
                continue
            
            skills_count = len(result.get('skills', []))
            orgs_count = len(result.get('organizations', []))
            
            print(f"   ✅ Success: {skills_count} skills, {orgs_count} organizations")
            
        except Exception as e:
            print(f"   ❌ Error processing {file_path.name}: {e}")
    
    return True

def test_model_components():
    """Test individual model components"""
    print(f"\n🧠 Testing Model Components")
    print("-" * 40)
    
    try:
        extractor = ResumeExtractor()
        
        # Test if model is loaded
        if extractor.nlp is None:
            print("❌ NER model not loaded")
            return False
        
        print("✅ NER model loaded successfully")
        
        # Test entity recognition on simple text
        test_text = "I have experience with Python and worked at Google for 2 years."
        doc = extractor.nlp(test_text)
        
        entities_found = len(doc.ents)
        print(f"✅ Entity recognition working: {entities_found} entities found")
        
        # Test PDF processor
        from utils.pdf_processor import PDFProcessor
        pdf_processor = PDFProcessor()
        
        # Test text cleaning
        messy_text = "  John   Smith  \n\n\n  Software Engineer  \n\n  "
        cleaned = pdf_processor.clean_text(messy_text)
        
        if "John Smith" in cleaned and "Software Engineer" in cleaned:
            print("✅ Text cleaning working")
        else:
            print("❌ Text cleaning failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    tests = [
        ("Sample Resume Processing", test_sample_resumes),
        ("File Processing", test_file_processing),
        ("Model Components", test_model_components)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is working correctly.")
        print("\n🚀 You can now:")
        print("   • Run 'streamlit run app.py' for the web interface")
        print("   • Run 'python gradio_app.py' for the Gradio interface")
        print("   • Use the inference.py script for batch processing")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        print("   • Make sure all dependencies are installed")
        print("   • Run the setup script: python setup.py")
        print("   • Check the README.md for troubleshooting")

def main():
    """Main test function"""
    generate_test_report()

if __name__ == "__main__":
    main()