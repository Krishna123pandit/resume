import streamlit as st
import os
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Setup Page
st.set_page_config(page_title="ATS Resume Expert", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Modern Professional Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Modern Light Background */
    .stApp {
        background-color: #FAFAFA;
        color: #111827;
    }
    
    /* Typography */
    .main-title {
        font-weight: 800;
        color: #111827;
        text-align: center;
        padding-bottom: 5px;
        margin-top: -20px;
        font-size: 3rem;
        letter-spacing: -0.03em;
    }
    .main-title span {
        color: #4F46E5;
    }
    .subtitle {
        color: #6B7280;
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 40px;
        font-weight: 400;
    }
    
    /* Input Elements */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        color: #111827 !important;
        padding: 16px !important;
        font-size: 1rem !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    .stTextArea textarea:focus {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }
    
    /* File Uploader */
    .stFileUploader > div > div {
        background-color: #FFFFFF !important;
        border: 2px dashed #D1D5DB !important;
        border-radius: 12px !important;
        padding: 24px !important;
        transition: all 0.2s ease-in-out;
    }
    .stFileUploader > div > div:hover {
        border-color: #4F46E5 !important;
        background-color: #F9FAFB !important;
    }
    
    /* Global Button Style */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 10px 20px;
        width: 100%;
        margin-top: 15px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Button 1: Evaluate (Modern Primary) */
    div[data-testid="column"]:nth-child(2) .stButton>button {
        background-color: #4F46E5;
        border: 1px solid #4F46E5;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2), 0 2px 4px -1px rgba(79, 70, 229, 0.1);
    }
    div[data-testid="column"]:nth-child(2) .stButton>button:hover {
        background-color: #4338CA;
        border-color: #4338CA;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(79, 70, 229, 0.3), 0 4px 6px -1px rgba(79, 70, 229, 0.2);
    }
    
    /* Button 2: Calculate Match (Modern Secondary Outline) */
    div[data-testid="column"]:nth-child(3) .stButton>button {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        color: #374151 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div[data-testid="column"]:nth-child(3) .stButton>button:hover {
        background-color: #F3F4F6;
        border-color: #D1D5DB;
        color: #111827 !important;
        transform: translateY(-1px);
    }
    
    /* Button 3: Suggest Roles (Modern Tertiary) */
    div[data-testid="column"]:nth-child(4) .stButton>button {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        color: #4F46E5 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div[data-testid="column"]:nth-child(4) .stButton>button:hover {
        background-color: #EEF2FF;
        border-color: #C7D2FE;
        transform: translateY(-1px);
    }

    /* Result Box */
    .result-box {
        background-color: #FFFFFF;
        border: 1px solid #F3F4F6;
        border-top: 4px solid #4F46E5;
        padding: 32px;
        border-radius: 12px;
        margin-top: 30px;
        font-size: 1rem;
        line-height: 1.7;
        color: #374151;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
    }
    
    /* Markdown styling inside result box */
    .result-box h1, .result-box h2, .result-box h3 {
        color: #111827;
        margin-top: 1.5em;
        margin-bottom: 0.75em;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    .result-box strong {
        color: #111827;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #F3F4F6;
    }
    </style>
""", unsafe_allow_html=True)

# 🔹 Gemini Response Function
def get_gemini_response(resume_text, prompt, input_text=None):
    if not api_key:
        return "Error: GOOGLE_API_KEY is not set in the .env file."
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        if input_text and input_text.strip():
            full_prompt = f"Job Description:\n{input_text}\n\nResume:\n{resume_text}\n\nTask: {prompt}"
        else:
            full_prompt = f"Resume:\n{resume_text}\n\nTask: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# 🔹 PDF Extraction
def extract_text_from_pdf(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

# 🔹 Sidebar
with st.sidebar:
    st.markdown("## ATS Resume Expert")
    st.markdown("Optimize your resume for the Applicant Tracking System (ATS) to improve your candidate profile.")
    st.markdown("---")
    st.markdown("### Instructions:")
    st.markdown("1. Enter **Job Description** (optional depending on task).")
    st.markdown("2. Upload **Resume (PDF)**.")
    st.markdown("3. Run an **Analysis Action**.")
    st.markdown("---")
    st.markdown("Powered by Streamlit & Gemini AI")

# 🔹 UI Layout
st.markdown("<div class='main-title'>Candidate <span>Evaluation</span> Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Optimize and evaluate candidate profiles against job requirements using AI.</div>", unsafe_allow_html=True)

# Status indicators
m1, m2, m3 = st.columns(3)
m1.metric(label="AI Engine", value="Gemini Flash")
m2.metric(label="API Status", value="Connected" if api_key else "Missing Key")
m3.metric(label="System Ready", value="Yes" if api_key else "No")

st.divider()

# 🔹 Main SaaS Workspace
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("### 📥 Data Input")
    with st.container(border=True):
        st.markdown("**1. Job Description** (Optional for Role Suggestion)")
        input_text = st.text_area("Paste the job description here...", height=200, label_visibility="collapsed")
        
        st.markdown("**2. Candidate Resume** (PDF Only)")
        uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"], label_visibility="collapsed")

with col_right:
    st.markdown("### ⚡ Analysis Actions")
    with st.container(border=True):
        st.markdown("Choose an AI analysis action to run against the provided data.")
        submit1 = st.button("🔍 Evaluate Candidate Fit", use_container_width=True)
        submit2 = st.button("📊 Calculate Match Score", use_container_width=True)
        submit3 = st.button("💡 Suggest Ideal Roles", use_container_width=True)

st.divider()

# Prompts
input_prompt1 = "Act as an experienced HR professional and ATS expert. Review the provided resume against the job description. Provide a detailed analysis of strengths, weaknesses, and a clear summary of how well the candidate fits the role."
input_prompt2 = "Act as an ATS expert. Calculate the percentage match between the resume and the job description. Provide the result as a percentage first, followed by a list of missing keywords and final recommendations."
input_prompt3 = "Act as an expert Career Counselor. Analyze the provided resume and suggest the top 3-5 job roles the candidate is best suited for. For each role, provide a brief explanation of why they are a good fit based on their skills and experience. Do not reference a job description as none is provided."

if submit1 or submit2 or submit3:
    st.markdown("### 📑 Analysis Report")
    with st.container(border=True):
        if not api_key:
            st.error("Please configure the GOOGLE_API_KEY in your environment to use AI features.")
        elif not uploaded_file:
            st.warning("Please upload a Candidate Resume (PDF) to proceed.")
        elif (submit1 or submit2) and not input_text:
            st.warning("Please provide a Job Description to perform a fit evaluation or calculate match percentage.")
        else:
            if submit1:
                prompt = input_prompt1
            elif submit2:
                prompt = input_prompt2
            else:
                prompt = input_prompt3
                
            with st.spinner("Analyzing profile data..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                
                # Pass input_text conditionally
                if submit3:
                    response = get_gemini_response(resume_text, prompt, input_text=None)
                else:
                    response = get_gemini_response(resume_text, prompt, input_text=input_text)
                
                st.markdown(f'<div class="result-box">\n\n{response}\n\n</div>', unsafe_allow_html=True)
