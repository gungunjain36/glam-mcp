MCP Server
A Media Conversion Pipeline (MCP) server built with FastAPI for video editing using FFmpeg. It accepts a video URL and a natural language prompt (e.g., "Cut from 10 to 20 seconds and apply sepia filter"), processes the prompt using the Gemini API, applies editing operations, and provides a download link.
Prerequisites

Python 3.6+ (Python Downloads)
FFmpeg installed at C:\Program Files\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin (Windows)
Gemini API key (Google AI Studio)
Virtual environment

Installation

Navigate to Project Directory:
cd glam-server


Create and Activate Virtual Environment:
python -m venv .venv
.venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure Gemini API Key:

Create a .env file in the project root:GEMINI_API_KEY=your-api-key


Replace your-api-key with your Gemini API key.


Verify FFmpeg:
"C:\Program Files\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe" -version



Running the Server
uvicorn src.main:app --reload

Usage
Send a POST request to http://localhost:8000/edit_video with a video URL and natural language prompt.
curl -X POST http://localhost:8000/edit_video -H "Content-Type: application/json" -d '{"url":"https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4","prompt":"Cut from 10 to 20 seconds and apply sepia filter"}'

Response: {"edited_video_url":"/download/<uuid>.mp4"}
Download the video:
curl http://localhost:8000/download/<uuid>.mp4 --output edited_video.mp4

Supported Operations

trim start end: Cuts video from start to end seconds.
crop w h x y: Crops to width w, height h, at (x, y).
filter name: Applies sepia or grayscale.

Notes

Edited videos are stored in output_videos/.
Only one trim operation is supported.
Requires a Gemini API key stored in .env for natural language processing.

License
MIT License
