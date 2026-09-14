import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from call_function import call_function

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

parser = argparse.ArgumentParser(description="AI Coding Agent")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
cli_args = parser.parse_args()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

Tool selection examples:
    "run main.py"                          -> run_python_file(file_path="main.py")
    "run tests.py"                         -> run_python_file(file_path="tests.py")
    "run main.py with 3 + 5"               -> run_python_file(file_path="main.py", args=["3 + 5"])
    "what files are in the calculator dir" -> get_files_info(directory="calculator")
    "show me the contents of main.py"      -> get_file_content(file_path="main.py")
    "create utils.py with a hello func"    -> write_file(file_path="utils.py", content="...")

All paths you provide should be relative to the working directory. You do not need to specify
the working directory in your function calls as it is automatically injected for security reasons.

When the user asks to run or execute a file, call run_python_file IMMEDIATELY.
Do not list or read files first.

When you think that you finish, just say "I fixed the bug ..."
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": cli_args.user_prompt},
]

available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
]

print(f"User: {cli_args.user_prompt}")

for _ in range(20):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=0,
        tools=available_functions,
    )

    if cli_args.verbose:
        print(f"User prompt: {cli_args.user_prompt}")
        if response.usage:
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)  # remember the assistant's tool-call turn

        # print()
        # for tool_call in message.tool_calls:

        result_message = call_function(tool_call=message.tool_calls[0], verbose=cli_args.verbose)

        # if not result_message.get("content"):
        #     raise Exception("Function call returned an empty result")
        # print(
        #     f"Tool: Here's the result of {message.tool_calls[0].function.name}...\n"
        #     # f"{result_message['content']}"
        #     )
        # print()
        # if cli_args.verbose:
            # print(f"-> {result_message['content']}")

        messages.append({
            "role": "tool",
            "tool_call_id": result_message["tool_call_id"],
            "content": result_message["content"],
        })
    else:
        print(f'Assistant: {message.content}')
        exit()
print(f"Agent reached the maximum number of iterations without results :(")
exit(1)
