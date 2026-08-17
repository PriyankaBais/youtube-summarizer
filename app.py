# import re
# import gradio as gr
# import streamlit as st
# from youtube_transcript_api import YouTubeTranscriptApi
# from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# model_name = "sshleifer/distilbart-cnn-12-6"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# summarizer = pipeline("text-generation", model=model, tokenizer=tokenizer)

# def extract_video_id(url):
#     regex = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
#     match = re.search(regex, url)
#     if match:
#         return match.group(1)
#     return None

# def summarize_youtube_video(youtube_url):
#     video_id = extract_video_id(youtube_url)
#     if not video_id:
#         return "Invalid YouTube URL. Please provide a valid link."
#     try:
#         ytt = YouTubeTranscriptApi()
#         transcript_list = ytt.fetch(video_id)
        
#         raw_text = " ".join([getattr(item, 'text', item.get('text') if isinstance(item, dict) else str(item)) for item in transcript_list])
        
#         max_chunk = 1000
#         words = raw_text.split()
#         chunks = [' '.join(words[i:i + max_chunk]) for i in range(0, len(words), max_chunk)]
        
#         summaries = []
#         for chunk in chunks:
#             summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
#             summaries.append(summary[0]['generated_text'])
            
#         return " ".join(summaries)
#     except Exception as e:
#         return f"Error processing video transcript: {str(e)}"

# demo = gr.Interface(
#     fn=summarize_youtube_video,
#     inputs=gr.Textbox(label="YouTube Video URL", placeholder="https://www.youtube.com/watch?v=..."),
#     outputs=gr.Textbox(label="Generated Summary", lines=10),
#     title="YouTube Video Summarizer",
#     description="Enter a YouTube video link to extract its transcript and generate an AI summary."
# )

# demo.launch(inline=True)
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
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    raw_text = " ".join([item['text'] for item in transcript_list])
                    
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
