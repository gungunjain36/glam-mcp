MCP Server
A Media Conversion Pipeline (MCP) server built with FastAPI for video editing using FFmpeg. It accepts a video URL and a text prompt (e.g., "trim 10 20; crop 100 100 0 0; filter sepia"), downloads the video, applies editing operations, and provides a download link.
Prerequisites

Python 3.6+ (Python Downloads)
FFmpeg installed and added to PATH (FFmpeg Installation)
Git (optional, for cloning)

Installation

Clone the Repository (if using Git):
git clone <repository-url>
cd mcp_server


Create and Activate a Virtual Environment:
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows


Install Dependencies:
pip install -r requirements.txt


Install FFmpeg:

Windows:
Download from gyan.dev (e.g., ffmpeg-release-full.7z).
Extract and add ffmpeg\bin to your system PATH.
Verify: ffmpeg -version


macOS:
Install via Homebrew: brew install ffmpeg
Verify: ffmpeg -version


Linux (Ubuntu/Debian):
Install: sudo apt update && sudo apt install ffmpeg
Verify: ffmpeg -version





Running the Server

Start the Server:
python src/main.py


The server runs on http://localhost:8000. Access the API documentation at http://localhost:8000/docs.


Usage
Send a POST request to /edit_video with a JSON body containing:

url: Direct URL to an MP4 video.
prompt: Editing instructions (e.g., "trim 10 20; crop 100 100 0 0; filter sepia").

Example:
curl -X POST http://localhost:8000/edit_video -H "Content-Type: application/json" -d '{"url":"http://example.com/sample.mp4","prompt":"trim 10 20; filter sepia"}'

Response:
{"edited_video_url":"/download/123e4567-e89b-12d3-a456-426614174000.mp4"}

Download the video at http://localhost:8000/download/<filename>.
Supported Operations

trim start end: Cuts video from start to end seconds (e.g., "trim 10 20").
crop w h x y: Crops to width w, height h, at position (x, y) (e.g., "crop 100 100 0 0").
filter name: Applies a filter (e.g., "filter sepia" or "filter grayscale").

Notes

Only one trim operation is supported.
Assumes direct MP4 URLs. For YouTube, integrate yt-dlp.
For production, use a WSGI server like Gunicorn and consider cloud storage (e.g., AWS S3).

License
MIT License
