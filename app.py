import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()

# Configure the Google Generative AI API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API key for Google Gemini not found. Please set the GEMINI_API_KEY environment variable.")
else:
    genai.configure(api_key=api_key)

# Define the prompt for summarizing YouTube transcripts
prompt = """You are a YouTube summarizer. You will be taking the transcript text, summarizing 
the entire video, and providing an important summary in points within 200 to 250 words. Please provide 
the summary of the text given here: """

# Function to extract transcript details from a YouTube video URL
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None
    except NoTranscriptFound:
        st.error("No transcript found for this video.")
        return None
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

# Function to generate summary content using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return None

# Streamlit app interface
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[-1]
    st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        if summary:
            st.markdown('## Detailed Notes:')
            st.write(summary)
        else:
            st.error("Failed to generate the summary.")
    else:
        st.error("Failed to extract the transcript.")
