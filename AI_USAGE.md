# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot): ChatGPT GPT-5

## Conversation links

- Link 1: https://chatgpt.com/share/6b0427cc-a810-83eb-bafe-846a71397930 

## What I used them for

- getting a suggestion of how to parse datetime in CSV file,  finishing implementation of 'parse_files' function correctly, breaking down the task into smaller tasks to get better vision of what to implement, understanding argparse and warnings logging, correctly using Path and JSONDecodeError

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| validator.py | parse_datetime() | mostly AI-generated code is used |
| csv_loader.py | parse_files() | AI-assisted - only partially generated code |
| flight_parser.py | create_parser() | mostly AI-generated code, but modified |
| flight_parser.py | make_log_handler() | AI-assisted - explained logger |
| flight_parser.py | read_json() | AI-assisted - explained JSONDecodeError |
| flight_parser.py | out_path in main() | AI-assisted - helped to implement output directory |

## Key prompts

1. How to parse datetime if value is a real date/time in the exact format?
2. How to set up argparse where exactly one of -i, -d or -j is required?
3. What's the cleanest way to turn json.JSONDecodeError into a short one-line error message?

## What I changed or verified myself

I verified and modified everything, least modified parts are connected to parsing datetime and argparse in flight_parser. AI helped me to get more clear vision of what to do in query.py file, so it suggested a structure and generated stub with constants, helper signatures, docstrings, and TODOs.