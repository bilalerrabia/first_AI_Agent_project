import os

def get_file_content(working_directory: str, file_path: str, max_chars: int = 10000) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

        is_within = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not is_within:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file) as f:
            content = f.read(max_chars)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {max_chars} characters]'
            return content
    except Exception as e:
        return f"Error: {e}"

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": (
            "Read the contents of a file within the working directory. "
            "Returns the file's text, up to a limit of 10,000 characters."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory.",
                },
            },
            "required": ["file_path"],
        },
    },
}