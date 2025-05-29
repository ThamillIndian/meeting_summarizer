import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Audio Processing App",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #ffcdd2;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎙️ Audio Processing App")
st.markdown("Upload an audio file to get transcription and analysis.")

# File uploader
uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a', 'ogg', 'flac'])

# API endpoint
API_URL = "http://127.0.0.1:8000/process-audio/"

# Process button
if uploaded_file is not None:
    if st.button("Process Audio"):
        try:
            # Show processing status
            with st.spinner("Processing audio file..."):
                # Prepare the file for upload
                files = {
                    "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                }
                
                # Make API request
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display success message
                    st.success("✅ Audio processed successfully!")
                    
                    # Display transcription in expandable section
                    with st.expander("📝 View Full Transcription"):
                        st.markdown(f"Word count: {result['word_count']}")
                        st.markdown("---")
                        st.markdown(result['transcription'])
                    
                else:
                    # Display error message
                    try:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Error: {error_detail}")
                    except:
                        st.error(f"Error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the API server. Please make sure the FastAPI server is running.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add footer with instructions
st.markdown("---")
st.markdown("""
    ### Instructions
    1. Upload an audio file (supported formats: WAV, MP3, M4A, OGG, FLAC)
    2. Click "Process Audio"
    3. View the results
""")

# Add a sidebar with information
with st.sidebar:
    st.title("About")
    st.markdown("""
        This application processes audio files to provide:
        - Transcription with word count
        - Basic analysis of content
    """)