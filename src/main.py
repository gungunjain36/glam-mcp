from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import tempfile
import os
import uuid
from src.config import OUTPUT_DIR
from src.operation_parser import parse_prompt
from src.ffmpeg_handler import generate_ffmpeg_command, run_ffmpeg_command

# Initialize FastAPI app
app = FastAPI()

# Define request model
class EditVideoRequest(BaseModel):
    url: str
    prompt: str

@app.post('/edit_video')
async def edit_video(data: EditVideoRequest):
    """
    Process video editing request.
    Args:
        data: JSON with video URL and prompt
    Returns:
        JSON with download URL for edited video
    """
    url = data.url
    prompt = data.prompt
    if not url or not prompt:
        raise HTTPException(status_code=400, detail="Missing url or prompt")

    # Download video
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            input_file = tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download video: {str(e)}")

    try:
        # Parse prompt
        ops = parse_prompt(prompt)
        # Generate output file name
        output_filename = f"{uuid.uuid4()}.mp4"
        output_file = os.path.join(OUTPUT_DIR, output_filename)
        # Generate and run FFmpeg command
        command = generate_ffmpeg_command(ops, input_file, output_file)
        run_ffmpeg_command(command)
        # Return download URL
        download_url = f"/download/{output_filename}"
        return {"edited_video_url": download_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(input_file)

@app.get('/download/{filename}')
async def download(filename: str):
    """
    Serve edited video for download.
    Args:
        filename: Name of the video file
    Returns:
        FileResponse with the video file
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)