# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Context Builder toolkit for extracting and contextualizing codebases for LLM interactions. It provides both basic command-line utilities and advanced interactive interfaces (CLI and web) for building optimized LLM prompts.

## Core Architecture

The project has three main components:

1. **Basic Context Builder** (`context_builder_basic.py`) - Simple command-line utility for basic code extraction
2. **Interactive Context Builder** (`context_builder.py`) - Advanced CLI with task-specific optimization
3. **Web Interface** (`context_web.py`) - Flask-based GUI for context building

### Key Classes and Components

- `ProjectAnalyzer` - Scans and analyzes project structure, identifies file types and main modules
- `ContextBuilder` - Builds structured context prompts with task-specific templates
- `ContextRequest` - Data class representing context building configuration
- `InteractiveCLI` - Provides interactive command-line interface

## Common Development Commands

### Basic Usage
```bash
# Basic context extraction
python context_builder_basic.py --root-dir ./my_project --output-file my_dump.md

# Interactive CLI
python context_builder.py /path/to/project

# Web interface
python context_builder.py --web
```

### Installation
```bash
pip install -r requirements.txt
```

### Testing the Web Interface
```bash
python context_web.py
# Opens on http://localhost:5000
```

## Task-Specific Context Types

The system supports 5 task types with specialized prompt templates:
- `add-feature` - For implementing new functionality
- `change-functionality` - For modifying existing behavior
- `explain-functionality` - For understanding specific features
- `explain-architecture` - For architectural overviews
- `debug-error` - For troubleshooting issues

## File Organization

- Source files are automatically categorized as: source, test, config, or documentation
- Default ignored directories: `.git`, `__pycache__`, `.pytest_cache`, `venv`, `.venv`, `node_modules`, `build`, `dist`, `target`
- Supported source extensions include most common programming languages (.py, .js, .ts, .java, .cpp, etc.)

## Web Interface Architecture

The Flask web app (`context_web.py`) provides:
- RESTful API endpoints (`/api/analyze`, `/api/build-context`)
- Dynamic HTML template generation
- File selection and preview capabilities
- Task-specific form fields that adapt based on selected task type