# 🎬 YouTube Video Summarizer AI

An AI-powered web application engineered to extract transcripts from YouTube videos and generate concise, coherent summaries using Hugging Face's `distilbart-cnn-12-6` Transformer model. Built with **Streamlit** and **yt-dlp**, this tool handles transcript extraction dynamically and bypasses cloud IP restrictions.

---

## 🚀 Live Demo

* **Live Web App:** [youtube-summarizer.streamlit.app](https://youtube-summarizer-9xv2juwyn6oanxu9idwwj3.streamlit.app/)
* **Repository:** [github.com/PriyankaBais/youtube-summarizer](https://github.com/PriyankaBais/youtube-summarizer)

---

## ✨ Features

* **Instant Transcript Extraction:** Leverages `yt-dlp` to fetch auto-generated or manual English subtitles directly from YouTube, bypassing standard cloud IP blocks.
* **Token-Safe Text Chunking:** Implements a dynamic word-chunking algorithm (300 words per window) to adhere to the model's 512-token sequence limit and prevent context overflow.
* **Transformer Summarization:** Utilizes Hugging Face's Serverless Inference API with `sshleifer/distilbart-cnn-12-6` for fast abstractive summarization.
* **Responsive Streamlit UI:** Minimalist and interactive interface with real-time progress indicators.
* **Lightweight & Cloud-Optimized:** Bypasses heavy local model weights (`PyTorch` / `transformers`), ensuring sub-second deployment builds and zero Out-Of-Memory (OOM) errors.

---

## 🛠️ Tech Stack

| Component | Technology / Library |
| :--- | :--- |
| **Frontend & UI** | Streamlit |
| **Transcript Engine** | `yt-dlp`, `requests`, `re` |
| **AI Inference Engine** | Hugging Face Serverless Inference API (`huggingface_hub`) |
| **Pre-trained Model** | `sshleifer/distilbart-cnn-12-6` |
| **Hosting & Deployment** | Streamlit Community Cloud |

---

## ⚙️ Architecture Workflow

1. **URL Parsing:** Extracts the unique 11-character YouTube Video ID from standard, short, or embedded links via Regex.
2. **Subtitle Extraction:** Calls `yt-dlp` to retrieve raw WebVTT/TTML subtitle tracks.
3. **Text Cleaning:** Strips WebVTT header tags, metadata, timestamps, and duplicated subtitle tracks.
4. **Sliding Window Chunking:** Divides the clean transcript into ~300-word blocks.
5. **API Inference:** Posts each block to Hugging Face Inference API sequentially.
6. **Reconstruction:** Aggregates individual chunk outputs and displays the final summary.

---

## 📁 Repository Structure

```text
youtube-summarizer/
├── app.py              # Main application logic & Streamlit UI
├── requirements.txt    # Application dependencies
└── README.md           # Project documentation
