"""
Generate sample resume data for training the NER model
"""
import os
import random
from typing import List, Dict

# Sample data for generating resumes
NAMES = [
    "John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "David Wilson",
    "Jessica Miller", "Christopher Taylor", "Amanda Anderson", "Matthew Thomas", "Ashley Jackson",
    "Daniel White", "Jennifer Harris", "James Martin", "Lisa Thompson", "Robert Garcia",
    "Mary Rodriguez", "William Martinez", "Elizabeth Robinson", "Joseph Clark", "Susan Lewis"
]

SKILLS = [
    "Python", "Java", "JavaScript", "C++", "React", "Node.js", "Angular", "Vue.js",
    "Machine Learning", "Deep Learning", "Data Science", "SQL", "MongoDB", "PostgreSQL",
    "AWS", "Azure", "Docker", "Kubernetes", "Git", "Jenkins", "TensorFlow", "PyTorch",
    "Pandas", "NumPy", "Scikit-learn", "HTML", "CSS", "Bootstrap", "Django", "Flask",
    "Spring Boot", "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "JIRA",
    "Linux", "Windows", "MacOS", "Bash", "PowerShell", "Tableau", "Power BI", "Excel"
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Apple", "Facebook", "Netflix", "Tesla", "Uber",
    "Airbnb", "Spotify", "Adobe", "Oracle", "IBM", "Intel", "NVIDIA", "Salesforce",
    "Twitter", "LinkedIn", "Dropbox", "Slack", "Zoom", "PayPal", "eBay", "Yahoo",
    "Cisco", "VMware", "Red Hat", "MongoDB", "Atlassian", "GitHub", "GitLab", "Docker"
]

UNIVERSITIES = [
    "Stanford University", "MIT", "Harvard University", "UC Berkeley", "Carnegie Mellon",
    "Georgia Tech", "University of Washington", "Cornell University", "Princeton University",
    "Yale University", "Columbia University", "University of Michigan", "UCLA", "USC",
    "University of Texas at Austin", "University of Illinois", "Purdue University",
    "Penn State", "Ohio State University", "University of Florida"
]

DEGREES = [
    "B.Tech in Computer Science", "B.S. in Computer Science", "M.S. in Computer Science",
    "B.Tech in Information Technology", "M.Tech in Computer Science", "MBA",
    "B.S. in Software Engineering", "M.S. in Data Science", "B.Tech in Electronics",
    "M.S. in Machine Learning", "Ph.D. in Computer Science", "B.S. in Mathematics",
    "M.S. in Artificial Intelligence", "B.Tech in Computer Engineering"
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "Full Stack Developer", "Backend Developer", "Frontend Developer", "DevOps Engineer",
    "Product Manager", "Technical Lead", "Software Architect", "Data Analyst",
    "AI Engineer", "Cloud Engineer", "Mobile Developer", "QA Engineer"
]

def generate_resume_text(name: str) -> str:
    """Generate a realistic resume text"""
    
    # Select random data
    selected_skills = random.sample(SKILLS, random.randint(5, 12))
    selected_companies = random.sample(COMPANIES, random.randint(1, 3))
    selected_university = random.choice(UNIVERSITIES)
    selected_degree = random.choice(DEGREES)
    selected_job_title = random.choice(JOB_TITLES)
    
    # Generate experience years
    total_exp = random.randint(1, 8)
    
    resume_text = f"""
{name}
Email: {name.lower().replace(' ', '.')}@email.com
Phone: +1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}

PROFESSIONAL SUMMARY
Experienced {selected_job_title} with {total_exp} years of experience in software development and technology.

EDUCATION
{selected_degree}
{selected_university}
Graduated: {random.randint(2015, 2023)}

TECHNICAL SKILLS
Programming Languages: {', '.join(selected_skills[:6])}
Technologies & Frameworks: {', '.join(selected_skills[6:])}

WORK EXPERIENCE
"""
    
    # Add work experience
    years_left = total_exp
    for i, company in enumerate(selected_companies):
        if years_left <= 0:
            break
            
        exp_years = min(random.randint(1, 3), years_left)
        start_year = 2024 - years_left
        end_year = start_year + exp_years
        
        resume_text += f"""
{selected_job_title}
{company}
{start_year} - {end_year} ({exp_years} years)
• Developed and maintained software applications using {random.choice(selected_skills[:3])}
• Collaborated with cross-functional teams to deliver high-quality solutions
• Implemented {random.choice(selected_skills[3:6])} for improved performance
"""
        years_left -= exp_years
    
    resume_text += f"""
PROJECTS
• Built a web application using {random.choice(selected_skills)} and {random.choice(selected_skills)}
• Developed machine learning models for data analysis using {random.choice(['Python', 'TensorFlow', 'PyTorch'])}
• Created REST APIs using {random.choice(['Django', 'Flask', 'Node.js', 'Spring Boot'])}

CERTIFICATIONS
• AWS Certified Solutions Architect
• Google Cloud Professional Data Engineer
"""
    
    return resume_text.strip()

def generate_sample_resumes(num_resumes: int = 100) -> None:
    """Generate sample resumes and save them as text files"""
    
    data_dir = "d:/.vscode/Resume_Extractor/data"
    resumes_dir = os.path.join(data_dir, "sample_resumes")
    
    # Create resumes directory
    os.makedirs(resumes_dir, exist_ok=True)
    
    # Generate resumes
    selected_names = random.sample(NAMES * 10, num_resumes)  # Allow duplicates with different surnames
    
    for i, base_name in enumerate(selected_names):
        # Add variation to names
        if i >= len(NAMES):
            surnames = ["Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez"]
            first_name = base_name.split()[0]
            surname = random.choice(surnames)
            name = f"{first_name} {surname}"
        else:
            name = base_name
            
        resume_text = generate_resume_text(name)
        
        # Save resume
        filename = f"resume_{i+1:03d}.txt"
        filepath = os.path.join(resumes_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(resume_text)
    
    print(f"Generated {num_resumes} sample resumes in {resumes_dir}")

if __name__ == "__main__":
    generate_sample_resumes(150)  # Generate 150 sample resumes