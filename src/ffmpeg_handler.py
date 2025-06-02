import subprocess
from src.operation_parser import operations

def generate_ffmpeg_command(ops: list, input_file: str, output_file: str) -> list:
    """
    Generate FFmpeg command to apply operations.
    Args:
        ops: List of operations from parse_prompt
        input_file: Path to input video
        output_file: Path to output video
    Returns:
        List of FFmpeg command arguments
    """
    command = ["ffmpeg", "-i", input_file]
    trim_set = False
    vf_filters = []
    for op in ops:
        if op["name"] == "trim":
            if trim_set:
                raise ValueError("Only one trim operation is supported")
            command += op["generate_options"](op["params"])
            trim_set = True
        elif op["name"] in ["crop", "filter"]:
            vf_filters.append(op["generate_options"](op["params"])[1])  # Extract -vf value
        else:
            raise ValueError(f"Unknown operation: {op['name']}")
    if vf_filters:
        command += ["-vf", ",".join(vf_filters)]
    command += ["-c:v", "libx264", "-crf", "23", "-c:a", "copy", "-y", output_file]
    return command

def run_ffmpeg_command(command: list) -> None:
    """
    Execute FFmpeg command and handle errors.
    Args:
        command: List of FFmpeg command arguments
    """
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")