"""
Context Builder

This script provides a command-line utility to scan a codebase, generate a visual directory
tree structure, and extract the contents of source files into a single Markdown file. This
output is especially useful for feeding into language models (LLMs) or for documentation purposes.

Features:
- Directory Tree Visualization: Generates a structured view of your codebase's directories.
- File Content Extraction: Scans and extracts contents from files with specific extensions.
- Flexible Filtering: Option to include or exclude specific files and directories.
- Markdown Output: Produces a well-formatted Markdown file that is easy to read and share.

Usage:
    python context_builder_basic.py --root-dir ./src --output-file context_dump.md

For additional options and usage details, run:
    python context_builder_basic.py --help
"""

import os
import argparse
from typing import List, Optional, Tuple


def generate_directory_tree(root_dir: str, ignored_dirs: List[str]) -> str:
    """
    Generates a visual directory tree structure for the project.
    
    Args:
        root_dir (str): The root directory of the project.
        ignored_dirs (List[str]): Directories to ignore while generating the tree.
        
    Returns:
        str: The directory tree as a formatted string.
    """
    tree: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
        
        # Calculate indentation level based on directory depth
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        tree.append(f"{indent}{os.path.basename(dirpath)}/")
        subindent = "    " * (level + 1)
        for filename in filenames:
            tree.append(f"{subindent}{filename}")
    return "\n".join(tree)


def scan_project(
    root_dir: str,
    file_extensions: Tuple[str, ...] = ('.py', '.js', '.html', '.css', '.json'),
    include_files: Optional[List[str]] = None,
    exclude_files: Optional[List[str]] = None,
    ignored_dirs: Optional[List[str]] = None
) -> str:
    """
    Scans the project and extracts the contents of files based on extension and filtering criteria.
    
    Args:
        root_dir (str): The root directory of the project.
        file_extensions (Tuple[str, ...]): File extensions to include by default.
        include_files (Optional[List[str]]): Specific file names to include (overrides exclude_files).
        exclude_files (Optional[List[str]]): Specific file names to exclude (ignored if include_files is specified).
        ignored_dirs (Optional[List[str]]): Directories to ignore while scanning.
        
    Returns:
        str: Concatenated content from the matching files, with file path headers.
    """
    all_code: List[str] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored directories
        if ignored_dirs:
            dirnames[:] = [d for d in dirnames if d not in ignored_dirs]

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            # Inclusion logic: if include_files is specified, only include those files
            if include_files and filename not in include_files:
                continue

            # Exclusion logic: if exclude_files is specified, skip those files
            if exclude_files and filename in exclude_files:
                continue

            # Default logic: if include_files is not specified, check if the file matches the extensions
            if not include_files and not filename.endswith(file_extensions):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    file_content = file.read()
                    all_code.append(f"```python\n# File: {file_path}\n{file_content}\n```\n")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    
    return "\n".join(all_code)


def write_to_file(output_path: str, content: str) -> None:
    """
    Writes the provided content to the specified output file.
    If the file already exists, it will be overwritten.
    
    Args:
        output_path (str): Path to the output file.
        content (str): Content to write.
    """
    # Remove the file if it exists to ensure a fresh write
    if os.path.exists(output_path):
        os.remove(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(content)


def main() -> None:
    """
    Parses command-line arguments, generates the directory tree and context dump,
    and writes the output to a Markdown file.
    """
    parser = argparse.ArgumentParser(
        description="Extract a project's directory structure and contents into a Markdown file for LLM prompts."
    )
    parser.add_argument(
        "--root-dir", type=str, default="./src",
        help="Root directory of the project to scan (default: './src')."
    )
    parser.add_argument(
        "--output-file", type=str, default="context_dump.md",
        help="Path to the output Markdown file (default: 'context_dump.md')."
    )
    parser.add_argument(
        "--include-files", type=str, nargs="*", default=None,
        help="List of specific file names to include (overrides exclusion and extension filtering)."
    )
    parser.add_argument(
        "--exclude-files", type=str, nargs="*", default=None,
        help="List of specific file names to exclude."
    )
    parser.add_argument(
        "--ignored-dirs", type=str, nargs="*", default=['.git', 'node_modules', 'venv', '__pycache__'],
        help="List of directory names to ignore while scanning (default: ['.git', 'node_modules', 'venv', '__pycache__'])."
    )
    parser.add_argument(
        "--extensions", type=str, nargs="*", default=['.py', '.js', '.html', '.css', '.json'],
        help="File extensions to include (default: .py, .js, .html, .css, .json)."
    )
    
    args = parser.parse_args()

    # Generate directory tree and scan project
    directory_tree = generate_directory_tree(args.root_dir, args.ignored_dirs)
    extracted_code = scan_project(
        root_dir=args.root_dir,
        file_extensions=tuple(args.extensions),
        include_files=args.include_files,
        exclude_files=args.exclude_files,
        ignored_dirs=args.ignored_dirs
    )

    # Combine the directory tree and the extracted code into a Markdown format
    final_output = (
        f"# Context Dump\n\n"
        f"## Directory Structure\n\n"
        f"```\n{directory_tree}\n```\n\n"
        f"## Project Content\n\n"
        f"{extracted_code}\n"
    )

    # Write the output to file
    write_to_file(args.output_file, final_output)
    print(f"Project context with directory structure dumped to {args.output_file}")


if __name__ == "__main__":
    main()
