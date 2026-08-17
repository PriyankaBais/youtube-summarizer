import re
import requests
import streamlit as st
import yt_dlp
from huggingface_hub import InferenceClient

hf_token = st.secrets.get("HF_TOKEN", None)
client = InferenceClient("sshleifer/distilbart-cnn-12-6", token=hf_token)

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer AI")
st.write("Enter a YouTube video link to extract its transcript and generate an AI summary.")

def extract_video_id(url):
    regex = r"(?:v=|\/|embed\/|watch\?v=|\&v=)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def fetch_transcript_ytdlp(video_url):
    ydl_opts = {
        'skip_download': True,
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['en', 'en-US'],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        subtitles = info.get('requested_subtitles') or info.get('subtitles') or info.get('automatic_captions')
        
        if not subtitles:
            raise Exception("No English subtitles or transcripts found for this video.")
            
        target_sub = subtitles.get('en') or subtitles.get('en-US') or list(subtitles.values())[0]
        if isinstance(target_sub, list):
            target_sub = target_sub[0]
            
        sub_url = target_sub.get('url')
        if not sub_url:
            raise Exception("Subtitle URL unavailable.")
            
        response = requests.get(sub_url)
        
        text_lines = []
        for line in response.text.splitlines():
            line = line.strip()
            if not line or '-->' in line or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            clean_line = re.sub(r'<[^>]+>', '', line).strip()
            if clean_line and (not text_lines or text_lines[-1] != clean_line):
                text_lines.append(clean_line)
                    
        return " ".join(text_lines)

youtube_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Summarize"):
    if not youtube_url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("Invalid YouTube URL.")
        else:
            with st.spinner("Fetching transcript and generating summary..."):
                try:
                    raw_text = fetch_transcript_ytdlp(youtube_url)
                    
                    if not raw_text.strip():
                        st.error("Could not extract readable text from transcript.")
                    else:
                        max_chunk = 300
                        words = raw_text.split()
                        chunks = [' '.join(words[i:i + max_chunk]) for i in range(0, len(words), max_chunk)]
                        
                        summaries = []
                        for chunk in chunks:
                            response = client.summarization(chunk)
                            summaries.append(response.summary_text)
                        
                        st.success("Summary Generated Successfully!")
                        st.subheader("Generated Summary")
                        st.write(" ".join(summaries))
                except Exception as e:
                    st.error(f"Error processing video transcript: {str(e)}")
