# Context Builder

**Context Builder** is a comprehensive toolkit for preparing codebase context for LLM interactions. It's designed for developers who need to manually extract and format code context when integrated agentic coding tools (like Claude Code, Cursor, etc.) aren't available or suitable for their environment.

## Features

### Basic Context Builder (`context_builder_basic.py`)
- **Directory Tree Visualization:** Generates a structured view of your codebase's directories
- **File Content Extraction:** Scans and extracts contents from files with specific extensions
- **Flexible Filtering:** Include or exclude specific files and directories
- **Markdown Output:** Produces a well-formatted Markdown file that's easy to read and share

### Interactive Context Builder (`context_builder.py`)
- **Project Analysis:** Automatically analyzes project structure and identifies key components
- **Task-Specific Contexts:** Optimizes prompts for different types of tasks:
  - Add new features
  - Change existing functionality
  - Explain functionality or architecture
  - Debug errors and issues
- **Smart File Selection:** Helps you choose the most relevant files for your task
- **Web Interface:** User-friendly Flask web GUI for building contexts
- **CLI Interface:** Interactive command-line interface for context building

## Requirements

- **Basic context builder:** Python 3.6+ (uses only standard library)
- **Interactive context builder:** Python 3.7+ + Flask 2.3.3
- Virtual environment is optional

## Installation

**Clone the repository:**
```bash
git clone https://github.com/yourusername/context-builder.git
cd context-builder
```

**For interactive context builder (optional):**
```bash
pip install -r requirements.txt
```

## Usage

### Basic Context Builder

Run the script from the command line:

```bash
python context_builder_basic.py --root-dir ./my_project --output-file my_dump.md
```

#### Command-Line Arguments

- `--root-dir`: Root directory of the codebase to scan (default: `./src`)
- `--output-file`: Path to the output Markdown file (default: `context_dump.md`)
- `--include-files`: Specific file names to include (overrides other filters)
- `--exclude-files`: Specific file names to exclude
- `--ignored-dirs`: Directories to exclude (default: `.git`, `node_modules`, `venv`, `__pycache__`)
- `--extensions`: File extensions to include (default: `.py`, `.js`, `.html`, `.css`, `.json`)

### Interactive Context Builder

#### Web Interface (Recommended)

Launch the web interface:
```bash
python context_builder.py --web
```

Then open your browser to `http://localhost:5000`

#### CLI Interface

Run the interactive CLI:
```bash
python context_builder.py /path/to/your/project
```

The CLI will guide you through:
1. Project analysis and file discovery
2. Task type selection (add feature, debug, explain, etc.)
3. File selection for optimal context
4. Context generation optimized for your specific task

### Examples

**Basic code dump:**
```bash
python context_builder_basic.py --root-dir ./my_react_app --extensions .js .jsx .css --output-file react_dump.md
```

**Interactive context for debugging:**
```bash
python context_builder.py ./my_project
# Select "Debug an error/issue" and follow the prompts
```

**Web interface for team collaboration:**
```bash
python context_builder.py --web
# Share http://localhost:5000 with your team
```

## Project Structure

```
context-builder/
├── context_builder_basic.py  # Basic context builder
├── context_builder.py        # Interactive context builder (CLI)
├── context_web.py            # Web interface for context builder
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web interface template
└── README.md                # This file
```

## Task-Specific Context Optimization

The interactive context builder creates optimized prompts for different scenarios:

- **Add Feature**: Includes project structure, existing patterns, and integration points
- **Change Functionality**: Focuses on current vs desired behavior analysis
- **Explain Functionality**: Provides step-by-step or high-level explanations
- **Explain Architecture**: Tailored for different audiences (developers, architects, stakeholders)
- **Debug Error**: Includes error context, reproduction steps, and expected behavior

## License

This project is licensed under the MIT License.