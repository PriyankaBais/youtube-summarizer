import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from huggingface_hub import InferenceClient

client = InferenceClient("sshleifer/distilbart-cnn-12-6")

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer AI")
st.write("Enter a YouTube video link to extract its transcript and generate an AI summary.")

def extract_video_id(url):
    regex = r"(?:v=|\/|embed\/|watch\?v=|\&v=)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    if hasattr(YouTubeTranscriptApi, 'get_transcript'):
        return YouTubeTranscriptApi.get_transcript(video_id)
    
    ytt = YouTubeTranscriptApi()
    if hasattr(ytt, 'fetch'):
        return ytt.fetch(video_id)
    return ytt.get_transcript(video_id)

youtube_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Summarize"):
    if not youtube_url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("Invalid YouTube URL. Please check the link.")
        else:
            with st.spinner("Fetching transcript and generating summary..."):
                try:
                    transcript_data = get_youtube_transcript(video_id)
                    raw_text = " ".join([
                        item.get('text', '') if isinstance(item, dict) else getattr(item, 'text', str(item))
                        for item in transcript_data
                    ])
                    
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
