# Filter map for video filters
filter_map = {
    "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
    "grayscale": "format=gray",
}

# Functions to generate FFmpeg options
def generate_trim_options(params):
    return ["-ss", params["start"], "-to", params["end"]]

def generate_crop_options(params):
    return ["-vf", f"crop={params['w']}:{params['h']}:{params['x']}:{params['y']}"]

def generate_filter_options(params):
    filter_str = filter_map.get(params["filter_name"])
    if filter_str is None:
        raise ValueError(f"Unknown filter: {params['filter_name']}")
    return ["-vf", filter_str]

# Supported operations
operations = [
    {
        "name": "trim",
        "params": ["start", "end"],
        "generate_options": generate_trim_options
    },
    {
        "name": "crop",
        "params": ["w", "h", "x", "y"],
        "generate_options": generate_crop_options
    },
    {
        "name": "filter",
        "params": ["filter_name"],
        "generate_options": generate_filter_options
    }
]

def parse_prompt(prompt: str) -> list:
    """
    Parse the prompt into a list of operations, including generate_options.
    Example: "trim 10 20; crop 100 100 0 0" -> [{"name": "trim", "params": {"start": "10", "end": "20"}, "generate_options": <function>}, ...]
    """
    operations_list = []
    for op_str in prompt.split(";"):
        parts = op_str.strip().split()
        if not parts:
            continue
        name = parts[0]
        params = parts[1:]
        op_def = next((op for op in operations if op["name"] == name), None)
        if op_def is None:
            raise ValueError(f"Unknown operation: {name}")
        if len(params) != len(op_def["params"]):
            raise ValueError(f"Operation {name} expects {len(op_def['params'])} parameters, got {len(params)}")
        param_dict = dict(zip(op_def["params"], params))
        operations_list.append({
            "name": name,
            "params": param_dict,
            "generate_options": op_def["generate_options"]
        })
    return operations_list