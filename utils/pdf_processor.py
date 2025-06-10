"""
PDF processing utilities for resume extraction
"""
import fitz  # PyMuPDF
import pdfminer
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import os
from typing import Optional, Union
from pathlib import Path

class PDFProcessor:
    """Handle PDF to text conversion using multiple methods"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt']
    
    def extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (fitz)"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting text with PyMuPDF: {e}")
            return ""
    
    def extract_text_pdfminer(self, pdf_path: str) -> str:
        """Extract text using pdfminer.six"""
        try:
            # Configure layout analysis parameters
            laparams = LAParams(
                boxes_flow=0.5,
                word_margin=0.1,
                char_margin=2.0,
                line_margin=0.5
            )
            
            text = extract_text(pdf_path, laparams=laparams)
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting text with pdfminer: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str, method: str = "pymupdf") -> str:
        """
        Extract text from PDF or text file
        
        Args:
            file_path: Path to the file
            method: Extraction method ('pymupdf' or 'pdfminer')
        
        Returns:
            Extracted text as string
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle text files
        if file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        
        # Handle PDF files
        elif file_path.suffix.lower() == '.pdf':
            if method == "pymupdf":
                text = self.extract_text_pymupdf(str(file_path))
                # Fallback to pdfminer if PyMuPDF fails
                if not text:
                    print("PyMuPDF failed, trying pdfminer...")
                    text = self.extract_text_pdfminer(str(file_path))
            else:
                text = self.extract_text_pdfminer(str(file_path))
                # Fallback to PyMuPDF if pdfminer fails
                if not text:
                    print("pdfminer failed, trying PyMuPDF...")
                    text = self.extract_text_pymupdf(str(file_path))
            
            return text
        
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        # Join lines with single newline
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text
    
    def process_resume_file(self, file_path: str, method: str = "pymupdf") -> str:
        """
        Process a resume file and return cleaned text
        
        Args:
            file_path: Path to resume file (PDF or TXT)
            method: PDF extraction method
        
        Returns:
            Cleaned text content
        """
        try:
            # Extract text
            raw_text = self.extract_text_from_file(file_path, method)
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            
            if not cleaned_text:
                raise ValueError("No text could be extracted from the file")
            
            return cleaned_text
        
        except Exception as e:
            raise Exception(f"Error processing resume file {file_path}: {e}")
    
    def batch_process_resumes(self, input_dir: str, output_dir: str = None) -> dict:
        """
        Process multiple resume files in a directory
        
        Args:
            input_dir: Directory containing resume files
            output_dir: Directory to save processed text files (optional)
        
        Returns:
            Dictionary mapping file names to extracted text
        """
        input_path = Path(input_dir)
        results = {}
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Create output directory if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Process all PDF and TXT files
        file_patterns = ['*.pdf', '*.txt']
        files_to_process = []
        
        for pattern in file_patterns:
            files_to_process.extend(input_path.glob(pattern))
        
        print(f"Found {len(files_to_process)} files to process")
        
        for file_path in files_to_process:
            try:
                print(f"Processing: {file_path.name}")
                
                # Extract text
                text = self.process_resume_file(str(file_path))
                results[file_path.name] = text
                
                # Save to output directory if specified
                if output_dir:
                    output_file = output_path / f"{file_path.stem}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                results[file_path.name] = ""
        
        print(f"Successfully processed {len([r for r in results.values() if r])} files")
        return results

# Example usage and testing
def test_pdf_processor():
    """Test the PDF processor with sample files"""
    processor = PDFProcessor()
    
    # Test with a sample text (simulating extracted PDF content)
    sample_text = """
    John Smith
    Software Engineer
    
    Email: john.smith@email.com
    Phone: +1-555-123-4567
    
    EXPERIENCE
    Senior Software Engineer
    Google Inc.
    2020 - Present (3 years)
    
    SKILLS
    Python, Java, Machine Learning, AWS, Docker
    
    EDUCATION
    B.Tech in Computer Science
    MIT
    2018
    """
    
    cleaned = processor.clean_text(sample_text)
    print("Cleaned text:")
    print(cleaned)
    print("\n" + "="*50)

if __name__ == "__main__":
    test_pdf_processor()