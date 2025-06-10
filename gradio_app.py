"""
Gradio interface for Resume Skill Extractor
"""
import gradio as gr
import json
import tempfile
import os
from pathlib import Path
from inference import ResumeExtractor

# Initialize the extractor
extractor = ResumeExtractor()

def process_resume_file(file_path):
    """Process uploaded resume file"""
    if file_path is None:
        return "Please upload a file first.", ""
    
    try:
        resume_info = extractor.process_resume_file(file_path)
        
        if "error" in resume_info:
            return f"Error: {resume_info['error']}", ""
        
        # Format the output
        output_text = f"""
📋 RESUME INFORMATION EXTRACTED

👤 Name: {resume_info.get('name', 'Not found')}
📧 Email: {resume_info.get('email', 'Not found')}
📞 Phone: {resume_info.get('phone', 'Not found')}
💼 Experience: {resume_info.get('experience', 'Not specified')}

🛠️ Skills ({len(resume_info.get('skills', []))}):
{chr(10).join(f"  • {skill}" for skill in resume_info.get('skills', []))}

🏢 Organizations ({len(resume_info.get('organizations', []))}):
{chr(10).join(f"  • {org}" for org in resume_info.get('organizations', []))}

🎓 Degrees ({len(resume_info.get('degrees', []))}):
{chr(10).join(f"  • {degree}" for degree in resume_info.get('degrees', []))}
"""
        
        # JSON output
        json_output = {
            "name": resume_info.get('name', ''),
            "skills": resume_info.get('skills', []),
            "experience": resume_info.get('experience', ''),
            "degree": resume_info.get('degrees', []),
            "organizations": resume_info.get('organizations', [])
        }
        
        return output_text, json.dumps(json_output, indent=2)
        
    except Exception as e:
        return f"Error processing file: {str(e)}", ""

def process_resume_text(text):
    """Process resume text directly"""
    if not text.strip():
        return "Please enter some resume text first.", ""
    
    try:
        resume_info = extractor.process_text(text)
        
        # Format the output
        output_text = f"""
📋 RESUME INFORMATION EXTRACTED

👤 Name: {resume_info.get('name', 'Not found')}
📧 Email: {resume_info.get('email', 'Not found')}
📞 Phone: {resume_info.get('phone', 'Not found')}
💼 Experience: {resume_info.get('experience', 'Not specified')}

🛠️ Skills ({len(resume_info.get('skills', []))}):
{chr(10).join(f"  • {skill}" for skill in resume_info.get('skills', []))}

🏢 Organizations ({len(resume_info.get('organizations', []))}):
{chr(10).join(f"  • {org}" for org in resume_info.get('organizations', []))}

🎓 Degrees ({len(resume_info.get('degrees', []))}):
{chr(10).join(f"  • {degree}" for degree in resume_info.get('degrees', []))}
"""
        
        # JSON output
        json_output = {
            "name": resume_info.get('name', ''),
            "skills": resume_info.get('skills', []),
            "experience": resume_info.get('experience', ''),
            "degree": resume_info.get('degrees', []),
            "organizations": resume_info.get('organizations', [])
        }
        
        return output_text, json.dumps(json_output, indent=2)
        
    except Exception as e:
        return f"Error processing text: {str(e)}", ""

# Sample resume text for demo
sample_resume = """John Smith
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
• Built web applications using React and Node.js"""

# Create Gradio interface
def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="Resume Skill Extractor",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .main-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 20px;
        }
        """
    ) as demo:
        
        gr.Markdown(
            """
            # 📄 Resume Skill Extractor
            ### Extract structured information from resumes using AI-powered NER
            
            Upload a resume file (PDF/TXT) or paste resume text to extract:
            - **Skills**: Technical and professional skills
            - **Experience**: Years of experience  
            - **Organizations**: Companies and universities
            - **Degrees**: Educational qualifications
            - **Contact Info**: Name, email, phone
            """,
            elem_classes=["main-header"]
        )
        
        with gr.Tabs():
            # File Upload Tab
            with gr.TabItem("📁 Upload File"):
                with gr.Row():
                    with gr.Column(scale=1):
                        file_input = gr.File(
                            label="Upload Resume (PDF or TXT)",
                            file_types=[".pdf", ".txt"],
                            type="filepath"
                        )
                        file_button = gr.Button("🔍 Extract Information", variant="primary")
                    
                    with gr.Column(scale=2):
                        file_output = gr.Textbox(
                            label="Extracted Information",
                            lines=20,
                            max_lines=30
                        )
                        file_json = gr.Code(
                            label="JSON Output",
                            language="json",
                            lines=10
                        )
                
                file_button.click(
                    fn=process_resume_file,
                    inputs=[file_input],
                    outputs=[file_output, file_json]
                )
            
            # Text Input Tab
            with gr.TabItem("📝 Paste Text"):
                with gr.Row():
                    with gr.Column(scale=1):
                        text_input = gr.Textbox(
                            label="Resume Text",
                            lines=15,
                            max_lines=20,
                            placeholder="Paste the complete resume text here...",
                            value=sample_resume
                        )
                        text_button = gr.Button("🔍 Extract Information", variant="primary")
                    
                    with gr.Column(scale=1):
                        text_output = gr.Textbox(
                            label="Extracted Information",
                            lines=20,
                            max_lines=30
                        )
                        text_json = gr.Code(
                            label="JSON Output",
                            language="json",
                            lines=10
                        )
                
                text_button.click(
                    fn=process_resume_text,
                    inputs=[text_input],
                    outputs=[text_output, text_json]
                )
        
        # Footer
        gr.Markdown(
            """
            ---
            ### 🔧 Model Information
            - **Model**: Custom spaCy NER trained on resume data
            - **Entities**: SKILL, ORG, DEGREE, DATE
            - **Supported Formats**: PDF, TXT
            
            ### 📚 Example Skills Detected
            Python, Java, Machine Learning, AWS, Docker, React, TensorFlow, etc.
            """
        )
    
    return demo

def main():
    """Launch the Gradio app"""
    print("Loading Resume Skill Extractor...")
    print("Model loaded successfully!")
    
    demo = create_interface()
    
    # Launch the app
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()