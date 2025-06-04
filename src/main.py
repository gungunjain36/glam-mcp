from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse
from pydantic import BaseModel
import requests
import tempfile
import os
import uuid
from src.config import OUTPUT_DIR
from src.operation_parser import parse_prompt
from src.ffmpeg_handler import generate_ffmpeg_command, run_ffmpeg_command
from src.gemini_handler import parse_natural_language

# Initialize FastAPI app
app = FastAPI()

# Define request model
class EditVideoRequest(BaseModel):
    url: str
    prompt: str

@app.post('/edit_video')
async def edit_video(data: EditVideoRequest):
    """
    Process video editing request with natural language prompt.
    Args:
        data: JSON with video URL and natural language prompt
    Returns:
        JSON with download URL for edited video
    """
    url = data.url
    natural_prompt = data.prompt
    if not url or not natural_prompt:
        raise HTTPException(status_code=400, detail="Missing url or prompt")

    # Convert natural language prompt to MCP-compatible prompt
    try:
        mcp_prompt = parse_natural_language(natural_prompt)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        # Parse MCP prompt
        ops = parse_prompt(mcp_prompt)
        # Generate output file name
        output_filename = f"{uuid.uuid4()}.mp4"
        output_file = os.path.join(OUTPUT_DIR, output_filename)
        # Generate and run FFmpeg command
        command = generate_ffmpeg_command(ops, input_file, output_file)
        run_ffmpeg_command(command)
        return {"edited_video_url": f"/download/{output_filename}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(input_file)

@app.get('/download/{filename}')
async def download_file(filename: str):
    """
    Download the edited video file.
    Args:
        filename: Name of the file to download
    Returns:
        File response
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='video/mp4', filename=filename)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)