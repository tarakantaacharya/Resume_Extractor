"""
Resume information extraction using trained NER model
"""
import spacy
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils.pdf_processor import PDFProcessor

class ResumeExtractor:
    """Extract structured information from resumes using trained NER model"""
    
    def __init__(self, model_path: str = "d:/.vscode/Resume_Extractor/models/resume_ner_model"):
        self.model_path = model_path
        self.nlp = None
        self.pdf_processor = PDFProcessor()
        self.load_model()
    
    def load_model(self):
        """Load the trained NER model"""
        try:
            model_path = Path(self.model_path)
            if model_path.exists():
                self.nlp = spacy.load(self.model_path)
                print(f"Loaded trained model from {self.model_path}")
            else:
                print(f"Trained model not found at {self.model_path}")
                print("Loading base model en_core_web_sm...")
                self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Loading base model en_core_web_sm...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                raise Exception("No spaCy model available. Please install en_core_web_sm or train the custom model first.")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using NER model"""
        doc = self.nlp(text)
        
        entities = {
            "skills": [],
            "organizations": [],
            "degrees": [],
            "dates": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                entities["skills"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "DEGREE":
                entities["degrees"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
        
        # Remove duplicates while preserving order
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))
        
        return entities
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex patterns"""
        contact_info = {
            "email": "",
            "phone": "",
            "name": ""
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group()
        
        # Extract phone
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact_info["phone"] = phone_match.group()
                break
        
        # Extract name (first line that looks like a name)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line.split()) <= 4:
                # Simple heuristic: 2-4 words, likely a name
                if not any(char.isdigit() for char in line) and '@' not in line:
                    contact_info["name"] = line
                    break
        
        return contact_info
    
    def calculate_experience(self, dates: List[str], text: str) -> str:
        """Calculate total experience from dates and text"""
        experience_years = 0
        
        # Look for explicit experience mentions
        exp_patterns = [
            r'(\d+)\s*\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\s*\+?\s*years?',
            r'(\d+)\s*years?\s+(?:of\s+)?(?:professional\s+)?experience'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                experience_years = max(experience_years, years)
        
        # Try to calculate from date ranges
        year_ranges = []
        for date in dates:
            # Look for year ranges like "2020-2023" or "2020-Present"
            range_match = re.search(r'(\d{4})\s*-\s*(?:(\d{4})|Present)', date)
            if range_match:
                start_year = int(range_match.group(1))
                end_year = int(range_match.group(2)) if range_match.group(2) else 2024
                year_ranges.append((start_year, end_year))
        
        # Calculate total experience from ranges
        if year_ranges:
            total_exp = sum(end - start for start, end in year_ranges)
            experience_years = max(experience_years, total_exp)
        
        if experience_years > 0:
            return f"{experience_years} years"
        else:
            return "Not specified"
    
    def extract_resume_info(self, text: str) -> Dict[str, Any]:
        """Extract all information from resume text"""
        # Extract entities using NER
        entities = self.extract_entities(text)
        
        # Extract contact information
        contact_info = self.extract_contact_info(text)
        
        # Calculate experience
        experience = self.calculate_experience(entities["dates"], text)
        
        # Combine all information
        resume_info = {
            "name": contact_info["name"],
            "email": contact_info["email"],
            "phone": contact_info["phone"],
            "skills": entities["skills"],
            "experience": experience,
            "organizations": entities["organizations"],
            "degrees": entities["degrees"],
            "dates": entities["dates"]
        }
        
        return resume_info
    
    def process_resume_file(self, file_path: str) -> Dict[str, Any]:
        """Process a resume file (PDF or TXT) and extract information"""
        try:
            # Extract text from file
            text = self.pdf_processor.process_resume_file(file_path)
            
            # Extract information
            resume_info = self.extract_resume_info(text)
            
            # Add metadata
            resume_info["source_file"] = Path(file_path).name
            resume_info["text_length"] = len(text)
            
            return resume_info
        
        except Exception as e:
            return {
                "error": str(e),
                "source_file": Path(file_path).name
            }
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process resume text directly and extract information"""
        return self.extract_resume_info(text)
    
    def batch_process_resumes(self, input_dir: str, output_file: str = None) -> List[Dict[str, Any]]:
        """Process multiple resume files and return results"""
        input_path = Path(input_dir)
        results = []
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all resume files
        file_patterns = ['*.pdf', '*.txt']
        files_to_process = []
        
        for pattern in file_patterns:
            files_to_process.extend(input_path.glob(pattern))
        
        print(f"Processing {len(files_to_process)} resume files...")
        
        for file_path in files_to_process:
            print(f"Processing: {file_path.name}")
            result = self.process_resume_file(str(file_path))
            results.append(result)
        
        # Save results if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {output_file}")
        
        return results
    
    def print_resume_info(self, resume_info: Dict[str, Any]):
        """Print resume information in a formatted way"""
        print("\n" + "="*60)
        print("RESUME INFORMATION EXTRACTION RESULTS")
        print("="*60)
        
        if "error" in resume_info:
            print(f"Error: {resume_info['error']}")
            return
        
        print(f"Name: {resume_info.get('name', 'Not found')}")
        print(f"Email: {resume_info.get('email', 'Not found')}")
        print(f"Phone: {resume_info.get('phone', 'Not found')}")
        print(f"Experience: {resume_info.get('experience', 'Not specified')}")
        
        print(f"\nSkills ({len(resume_info.get('skills', []))}):")
        for skill in resume_info.get('skills', []):
            print(f"  • {skill}")
        
        print(f"\nOrganizations ({len(resume_info.get('organizations', []))}):")
        for org in resume_info.get('organizations', []):
            print(f"  • {org}")
        
        print(f"\nDegrees ({len(resume_info.get('degrees', []))}):")
        for degree in resume_info.get('degrees', []):
            print(f"  • {degree}")
        
        if resume_info.get('dates'):
            print(f"\nDates:")
            for date in resume_info.get('dates', []):
                print(f"  • {date}")

def main():
    """Main function for testing the extractor"""
    extractor = ResumeExtractor()
    
    # Test with sample text
    sample_resume = """
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
    
    print("Testing Resume Extractor...")
    result = extractor.process_text(sample_resume)
    extractor.print_resume_info(result)
    
    # Also return JSON format
    print(f"\nJSON Output:")
    json_output = {
        "name": result.get('name', ''),
        "skills": result.get('skills', []),
        "experience": result.get('experience', ''),
        "degree": result.get('degrees', [])
    }
    print(json.dumps(json_output, indent=2))

if __name__ == "__main__":
    main()