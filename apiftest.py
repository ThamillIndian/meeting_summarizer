import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
import logging

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Constants
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
API_TIMEOUT = 300  # 5 minutes

# Validate API Key
if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY. Please check your .env file.")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client with timeout
client = Groq(api_key=GROQ_API_KEY, timeout=API_TIMEOUT)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"message": "API is running successfully!"}

def process_with_groq(file_content: bytes) -> dict:
    """Process content with Groq API"""
    try:
        # Create prompt for transcription and analysis
        prompt = """
        Please provide:
        1. A transcription of the audio content
        2. A brief summary of the main points
        3. Key action items or decisions (if any)
        """

        # Call Groq API
        response = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes audio content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        result = response.choices[0].message.content.strip()
        return {
            "transcription": result,
            "word_count": len(result.split())
        }
    except Exception as e:
        logger.error(f"Groq API processing failed: {str(e)}")
        raise

@app.post("/process-audio/")
async def process_audio(
    request: Request,
    file: UploadFile = File(...)
):
    """Process uploaded audio file with Groq API"""
    try:
        # Validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB")

        # Validate file extension
        allowed_extensions = {"wav", "mp3", "m4a", "ogg", "flac"}
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")

        logger.info(f"📂 Processing file: {file.filename}")

        # Process with Groq API
        result = process_with_groq(file_content)
        logger.info("✅ Processing completed")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")