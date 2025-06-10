"""
Streamlit web application for Resume Skill Extractor
"""
import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from inference import ResumeExtractor
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Resume Skill Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .skill-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    .org-tag {
        background-color: #f3e5f5;
        color: #4a148c;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    .degree-tag {
        background-color: #e8f5e8;
        color: #1b5e20;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_extractor():
    """Load the resume extractor (cached)"""
    return ResumeExtractor()

def display_resume_info(resume_info):
    """Display extracted resume information in a formatted way"""
    if "error" in resume_info:
        st.error(f"Error processing resume: {resume_info['error']}")
        return
    
    # Basic Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Basic Information")
        st.write(f"**Name:** {resume_info.get('name', 'Not found')}")
        st.write(f"**Email:** {resume_info.get('email', 'Not found')}")
        st.write(f"**Phone:** {resume_info.get('phone', 'Not found')}")
        st.write(f"**Experience:** {resume_info.get('experience', 'Not specified')}")
    
    with col2:
        st.subheader("🎓 Education")
        degrees = resume_info.get('degrees', [])
        if degrees:
            for degree in degrees:
                st.markdown(f'<span class="degree-tag">{degree}</span>', unsafe_allow_html=True)
        else:
            st.write("No degrees found")
    
    # Skills
    st.subheader("🛠️ Technical Skills")
    skills = resume_info.get('skills', [])
    if skills:
        skills_html = ""
        for skill in skills:
            skills_html += f'<span class="skill-tag">{skill}</span>'
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.write("No skills found")
    
    # Organizations
    st.subheader("🏢 Organizations")
    organizations = resume_info.get('organizations', [])
    if organizations:
        orgs_html = ""
        for org in organizations:
            orgs_html += f'<span class="org-tag">{org}</span>'
        st.markdown(orgs_html, unsafe_allow_html=True)
    else:
        st.write("No organizations found")
    
    # JSON Output
    with st.expander("📄 View JSON Output"):
        json_output = {
            "name": resume_info.get('name', ''),
            "skills": resume_info.get('skills', []),
            "experience": resume_info.get('experience', ''),
            "degree": resume_info.get('degrees', []),
            "organizations": resume_info.get('organizations', [])
        }
        st.json(json_output)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Skill Extractor</h1>', unsafe_allow_html=True)
    st.markdown("**Extract structured information from resumes using AI-powered NER**")
    
    # Sidebar
    st.sidebar.title("🔧 Options")
    
    # Load extractor
    with st.spinner("Loading AI model..."):
        extractor = load_extractor()
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["Upload File", "Paste Text", "Batch Processing"]
    )
    
    if input_method == "Upload File":
        st.subheader("📁 Upload Resume File")
        
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'txt'],
            help="Upload a PDF or text file containing the resume"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                with st.spinner("Extracting information from resume..."):
                    resume_info = extractor.process_resume_file(tmp_file_path)
                
                st.success("✅ Resume processed successfully!")
                display_resume_info(resume_info)
                
            except Exception as e:
                st.error(f"Error processing file: {e}")
            
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
    
    elif input_method == "Paste Text":
        st.subheader("📝 Paste Resume Text")
        
        resume_text = st.text_area(
            "Paste the resume text here:",
            height=300,
            placeholder="Paste the complete resume text here..."
        )
        
        if st.button("🔍 Extract Information"):
            if resume_text.strip():
                with st.spinner("Extracting information from text..."):
                    resume_info = extractor.process_text(resume_text)
                
                st.success("✅ Text processed successfully!")
                display_resume_info(resume_info)
            else:
                st.warning("Please paste some resume text first.")
    
    elif input_method == "Batch Processing":
        st.subheader("📁 Batch Process Multiple Resumes")
        
        st.info("Upload multiple resume files to process them all at once.")
        
        uploaded_files = st.file_uploader(
            "Choose resume files",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple PDF or text files"
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} files")
            
            if st.button("🔍 Process All Resumes"):
                results = []
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    # Update progress
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    # Save file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        resume_info = extractor.process_resume_file(tmp_file_path)
                        resume_info['filename'] = uploaded_file.name
                        results.append(resume_info)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")
                    finally:
                        if os.path.exists(tmp_file_path):
                            os.unlink(tmp_file_path)
                
                # Display results
                st.success(f"✅ Processed {len(results)} resumes!")
                
                # Create summary table
                summary_data = []
                for result in results:
                    if "error" not in result:
                        summary_data.append({
                            "Filename": result.get('filename', ''),
                            "Name": result.get('name', 'Not found'),
                            "Skills Count": len(result.get('skills', [])),
                            "Experience": result.get('experience', 'Not specified'),
                            "Organizations": len(result.get('organizations', [])),
                            "Degrees": len(result.get('degrees', []))
                        })
                
                if summary_data:
                    df = pd.DataFrame(summary_data)
                    st.subheader("📊 Summary Table")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download results as JSON
                    json_results = json.dumps(results, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download Results as JSON",
                        data=json_results,
                        file_name="resume_extraction_results.json",
                        mime="application/json"
                    )
                
                # Show individual results
                with st.expander("📄 View Individual Results"):
                    for i, result in enumerate(results):
                        st.subheader(f"Resume {i+1}: {result.get('filename', 'Unknown')}")
                        display_resume_info(result)
                        st.divider()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 About")
    st.sidebar.markdown("""
    This application uses a custom-trained NER model to extract:
    - **Skills**: Technical and professional skills
    - **Experience**: Years of experience
    - **Organizations**: Companies and universities
    - **Degrees**: Educational qualifications
    - **Contact Info**: Name, email, phone
    """)
    
    st.sidebar.markdown("### 🔧 Model Info")
    st.sidebar.markdown(f"""
    - **Model**: Custom spaCy NER
    - **Entities**: SKILL, ORG, DEGREE, DATE
    - **Input**: PDF, TXT files
    """)

if __name__ == "__main__":
    main()