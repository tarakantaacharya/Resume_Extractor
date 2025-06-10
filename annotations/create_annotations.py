"""
Create training annotations for NER model
"""
import os
import re
import json
import random
from typing import List, Tuple, Dict, Any
from pathlib import Path

class ResumeAnnotator:
    def __init__(self):
        # Define entity patterns
        self.skill_patterns = [
            r'\b(?:Python|Java|JavaScript|C\+\+|React|Node\.js|Angular|Vue\.js)\b',
            r'\b(?:Machine Learning|Deep Learning|Data Science|SQL|MongoDB|PostgreSQL)\b',
            r'\b(?:AWS|Azure|Docker|Kubernetes|Git|Jenkins|TensorFlow|PyTorch)\b',
            r'\b(?:Pandas|NumPy|Scikit-learn|HTML|CSS|Bootstrap|Django|Flask)\b',
            r'\b(?:Spring Boot|REST API|GraphQL|Microservices|Agile|Scrum|JIRA)\b',
            r'\b(?:Linux|Windows|MacOS|Bash|PowerShell|Tableau|Power BI|Excel)\b'
        ]
        
        self.org_patterns = [
            r'\b(?:Google|Microsoft|Amazon|Apple|Facebook|Netflix|Tesla|Uber)\b',
            r'\b(?:Airbnb|Spotify|Adobe|Oracle|IBM|Intel|NVIDIA|Salesforce)\b',
            r'\b(?:Twitter|LinkedIn|Dropbox|Slack|Zoom|PayPal|eBay|Yahoo)\b',
            r'\b(?:Stanford University|MIT|Harvard University|UC Berkeley|Carnegie Mellon)\b',
            r'\b(?:Georgia Tech|University of Washington|Cornell University|Princeton University)\b',
            r'\b(?:Yale University|Columbia University|University of Michigan|UCLA|USC)\b'
        ]
        
        self.degree_patterns = [
            r'\b(?:B\.Tech|B\.S\.|M\.S\.|M\.Tech|MBA|Ph\.D\.)\s+(?:in\s+)?(?:Computer Science|Information Technology|Software Engineering|Data Science|Electronics|Machine Learning|Artificial Intelligence|Mathematics|Computer Engineering)\b',
            r'\b(?:Bachelor|Master|Doctor)\s+of\s+(?:Science|Technology|Arts|Engineering)\s+(?:in\s+)?(?:Computer Science|Information Technology|Software Engineering)\b'
        ]
        
        self.date_patterns = [
            r'\b\d{4}\s*-\s*\d{4}\b',
            r'\b\d{4}\s*-\s*Present\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',
            r'\b\d+\s+years?\b',
            r'\b\d+\s+months?\b'
        ]
    
    def find_entities(self, text: str) -> List[Tuple[int, int, str]]:
        """Find entities in text and return their positions and labels"""
        entities = []
        
        # Find SKILL entities
        for pattern in self.skill_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append((match.start(), match.end(), "SKILL"))
        
        # Find ORG entities
        for pattern in self.org_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append((match.start(), match.end(), "ORG"))
        
        # Find DEGREE entities
        for pattern in self.degree_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append((match.start(), match.end(), "DEGREE"))
        
        # Find DATE entities
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append((match.start(), match.end(), "DATE"))
        
        # Remove overlapping entities (keep the longest one)
        entities = self.remove_overlapping_entities(entities)
        
        return entities
    
    def remove_overlapping_entities(self, entities: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
        """Remove overlapping entities, keeping the longest ones"""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda x: x[0])
        
        filtered_entities = []
        for entity in entities:
            start, end, label = entity
            
            # Check if this entity overlaps with any already added entity
            overlaps = False
            for existing_start, existing_end, _ in filtered_entities:
                if (start < existing_end and end > existing_start):
                    # There's an overlap
                    if (end - start) <= (existing_end - existing_start):
                        # Current entity is shorter or equal, skip it
                        overlaps = True
                        break
                    else:
                        # Current entity is longer, remove the existing one
                        filtered_entities = [(s, e, l) for s, e, l in filtered_entities 
                                           if not (s == existing_start and e == existing_end)]
            
            if not overlaps:
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def create_training_data(self, text: str) -> Tuple[str, Dict[str, List[Tuple[int, int, str]]]]:
        """Create training data in spaCy format"""
        entities = self.find_entities(text)
        return (text, {"entities": entities})
    
    def annotate_resumes(self, resumes_dir: str, output_file: str) -> None:
        """Annotate all resumes and save training data"""
        training_data = []
        
        resumes_path = Path(resumes_dir)
        if not resumes_path.exists():
            print(f"Directory {resumes_dir} does not exist!")
            return
        
        resume_files = list(resumes_path.glob("*.txt"))
        print(f"Found {len(resume_files)} resume files")
        
        for resume_file in resume_files:
            try:
                with open(resume_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                training_example = self.create_training_data(text)
                training_data.append(training_example)
                
            except Exception as e:
                print(f"Error processing {resume_file}: {e}")
        
        # Save training data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created {len(training_data)} training examples")
        print(f"Training data saved to {output_file}")
        
        # Print statistics
        self.print_annotation_stats(training_data)
    
    def print_annotation_stats(self, training_data: List[Tuple[str, Dict]]) -> None:
        """Print statistics about the annotations"""
        entity_counts = {"SKILL": 0, "ORG": 0, "DEGREE": 0, "DATE": 0}
        
        for text, annotations in training_data:
            for start, end, label in annotations["entities"]:
                entity_counts[label] += 1
        
        print("\nAnnotation Statistics:")
        for label, count in entity_counts.items():
            print(f"{label}: {count} entities")
        
        total_entities = sum(entity_counts.values())
        print(f"Total entities: {total_entities}")

def main():
    """Main function to create annotations"""
    annotator = ResumeAnnotator()
    
    # Paths
    resumes_dir = "d:/.vscode/Resume_Extractor/data/sample_resumes"
    output_file = "d:/.vscode/Resume_Extractor/annotations/training_data.json"
    
    # Create annotations
    annotator.annotate_resumes(resumes_dir, output_file)

if __name__ == "__main__":
    main()