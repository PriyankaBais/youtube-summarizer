import re
import requests
import io
import streamlit as st
import yt_dlp
from huggingface_hub import InferenceClient

client = InferenceClient("sshleifer/distilbart-cnn-12-6")

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer AI")
st.write("Extract and summarize YouTube videos instantly using AI.")

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
            raise Exception("No English subtitles found for this video.")
            
        target_sub = subtitles.get('en') or subtitles.get('en-US') or list(subtitles.values())[0]
        if isinstance(target_sub, list):
            target_sub = target_sub[0]
            
        sub_url = target_sub.get('url')
        if not sub_url:
            raise Exception("Subtitle URL unavailable.")
            
        import requests
        response = requests.get(sub_url)
        
        text_lines = []
        for line in response.text.splitlines():
            if '-->' not in line and line.strip() and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:'):
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
                    
                    max_chunk = 1000
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
