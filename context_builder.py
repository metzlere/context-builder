"""
Interactive Context Builder
Provides both CLI and Flask web interfaces for building optimized LLM contexts
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ContextRequest:
    """Represents a context building request"""
    project_path: str
    task_type: str  # add-feature, change-functionality, explain-functionality, explain-architecture, debug-error
    description: str
    selected_files: List[str]
    include_docs: bool = True
    focus_area: Optional[str] = None
    # Task-specific fields
    requirements: Optional[str] = None
    current_behavior: Optional[str] = None
    desired_behavior: Optional[str] = None
    explanation_level: Optional[str] = None
    audience: Optional[str] = None
    error_message: Optional[str] = None
    error_context: Optional[str] = None
    expected_behavior: Optional[str] = None

class ProjectAnalyzer:
    """Analyzes projects and suggests context strategies"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.source_files = []
        self.test_files = []
        self.config_files = []
        self.doc_files = []
        
    def analyze(self) -> Dict:
        """Analyze the project structure"""
        self._scan_project()
        
        return {
            'project_name': self.project_path.name,
            'source_files': [str(f.relative_to(self.project_path)) for f in self.source_files],
            'test_files': [str(f.relative_to(self.project_path)) for f in self.test_files],
            'config_files': [str(f.relative_to(self.project_path)) for f in self.config_files],
            'doc_files': [str(f.relative_to(self.project_path)) for f in self.doc_files],
            'structure': self._build_structure(),
            'main_modules': self._identify_main_modules()
        }
    
    def _scan_project(self):
        """Scan project for different file types"""
        ignore_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules', 'build', 'dist', 'target'}
        
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.r', '.m', '.mm', '.sh', '.bat', '.ps1', '.vue', '.html', '.css', '.scss', '.sass', '.less', '.sql', '.pl', '.lua', '.dart', '.elm', '.fs', '.fsx', '.fsi', '.ml', '.mli', '.hs', '.ex', '.exs', '.clj', '.cljs', '.cljc', '.nim', '.cr', '.zig', '.jl', '.v', '.vb', '.pas', '.d', '.groovy', '.gradle', '.makefile', '.cmake', '.dockerfile'}
        
        config_files = {'package.json', 'requirements.txt', 'setup.py', 'pyproject.toml', 'setup.cfg', 'pom.xml', 'build.gradle', 'CMakeLists.txt', 'Makefile', 'Dockerfile', 'docker-compose.yml', 'config.json', 'settings.json', '.env', '.gitignore', '.eslintrc', '.prettierrc', 'tsconfig.json', 'webpack.config.js', 'babel.config.js', 'jest.config.js', 'cargo.toml', 'go.mod', 'composer.json', 'gemfile', 'podfile'}
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                file_lower = file.lower()
                
                # Check if it's a source file
                if any(file_lower.endswith(ext) for ext in source_extensions) or file_lower == 'makefile':
                    if 'test' in file_lower or 'spec' in file_lower or '/test' in str(file_path).lower():
                        self.test_files.append(file_path)
                    else:
                        self.source_files.append(file_path)
                elif file_lower in config_files or file_lower.startswith('.') and file_lower.endswith('rc'):
                    self.config_files.append(file_path)
                elif file_lower.endswith(('.md', '.rst', '.txt', '.adoc', '.org')):
                    self.doc_files.append(file_path)
    
    def _build_structure(self) -> str:
        """Build directory structure string as markdown tree"""
        structure = []
        
        # Build a tree structure with proper markdown formatting
        def build_tree(path, prefix="", is_last=True):
            if len(Path(path).relative_to(self.project_path).parts) > 3:  # Limit depth
                return
                
            # Get directory name
            dir_name = os.path.basename(path)
            if path == self.project_path:
                dir_name = self.project_path.name
                
            # Directory symbol
            connector = "└── " if is_last else "├── "
            structure.append(f"{prefix}{connector}📁 {dir_name}/")
            
            # Update prefix for children
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Get subdirectories and files
            try:
                items = os.listdir(path)
                # Filter out hidden directories and common build/cache directories
                ignore_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules', 'build', 'dist', 'target'}
                dirs = [d for d in items if os.path.isdir(os.path.join(path, d)) and d not in ignore_dirs]
                
                # Get source files
                source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.r', '.m', '.mm', '.sh', '.bat', '.ps1', '.vue', '.html', '.css', '.scss', '.sass', '.less', '.sql', '.pl', '.lua', '.dart', '.elm', '.fs', '.fsx', '.fsi', '.ml', '.mli', '.hs', '.ex', '.exs', '.clj', '.cljs', '.cljc', '.nim', '.cr', '.zig', '.jl', '.v', '.vb', '.pas', '.d', '.groovy', '.gradle', '.makefile', '.cmake', '.dockerfile'}
                files = [f for f in items if os.path.isfile(os.path.join(path, f)) and 
                        (any(f.lower().endswith(ext) for ext in source_extensions) or f.lower() == 'makefile')]
                
                # Sort directories and files
                dirs.sort()
                files.sort()
                
                # Limit files shown per directory
                files = files[:5]
                
                # Show directories first
                for i, dir_name in enumerate(dirs):
                    dir_path = os.path.join(path, dir_name)
                    is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                    build_tree(dir_path, new_prefix, is_last_dir)
                
                # Then show files
                for i, file_name in enumerate(files):
                    is_last_file = (i == len(files) - 1)
                    file_connector = "└── " if is_last_file else "├── "
                    
                    # Choose appropriate emoji based on file type
                    ext = os.path.splitext(file_name)[1].lower()
                    emoji = "🐍" if ext == '.py' else "📄"
                    
                    structure.append(f"{new_prefix}{file_connector}{emoji} {file_name}")
                
                # Show truncation message if there are more files
                if len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and 
                       (any(f.lower().endswith(ext) for ext in source_extensions) or f.lower() == 'makefile')]) > 5:
                    remaining = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and 
                                   (any(f.lower().endswith(ext) for ext in source_extensions) or f.lower() == 'makefile')]) - 5
                    structure.append(f"{new_prefix}    ⋮ ({remaining} more files)")
                    
            except PermissionError:
                pass
        
        build_tree(str(self.project_path))
        return "\n".join(structure)
    
    def _identify_main_modules(self) -> List[str]:
        """Identify main modules/entry points"""
        main_modules = []
        
        for source_file in self.source_files:
            name = source_file.stem.lower()
            if name in ['main', 'app', '__main__', 'run', 'server', 'index', 'start', 'launch', 'program']:
                main_modules.append(str(source_file.relative_to(self.project_path)))
        
        return main_modules

class ContextBuilder:
    """Builds structured context for LLM prompts"""
    
    TASK_TEMPLATES = {
        'add-feature': {
            'title': 'Feature Development',
            'intro': 'I want to add a new feature to my project.',
            'focus': 'Please help me implement this feature following the existing patterns.'
        },
        'change-functionality': {
            'title': 'Functionality Change',
            'intro': 'I want to change how something currently works.',
            'focus': 'Please help me modify the existing functionality.'
        },
        'explain-functionality': {
            'title': 'Functionality Explanation',
            'intro': 'I need help understanding how specific functionality works.',
            'focus': 'Please explain how this functionality operates.'
        },
        'explain-architecture': {
            'title': 'Architecture Explanation',
            'intro': 'I need help understanding the overall architecture.',
            'focus': 'Please explain the architectural design and component relationships.'
        },
        'debug-error': {
            'title': 'Debug Assistance',
            'intro': 'I need help debugging an error or issue.',
            'focus': 'Please analyze the code and help identify the problem.'
        }
    }
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analyzer = ProjectAnalyzer(project_path)
        
    def build_context(self, request: ContextRequest) -> str:
        """Build complete context prompt"""
        analysis = self.analyzer.analyze()
        template = self.TASK_TEMPLATES[request.task_type]
        
        # Build sections
        sections = []
        
        # Header
        sections.append(f"# {template['title']}\n")
        sections.append(f"{template['intro']}\n")
        sections.append(f"**Task**: {request.description}\n")
        
        # Project Overview
        sections.append("## Project Overview")
        sections.append(f"**Project**: {analysis['project_name']}")
        sections.append(f"**Source Files**: {len(analysis['source_files'])}")
        sections.append(f"**Test Files**: {len(analysis['test_files'])}")
        if analysis['main_modules']:
            sections.append(f"**Main Modules**: {', '.join(analysis['main_modules'])}")
        sections.append("")
        
        # Architecture
        sections.append("## Project Structure")
        sections.append("```")
        sections.append(analysis['structure'])
        sections.append("```\n")
        
        # Selected Code
        if request.selected_files:
            sections.append("## Selected Code")
            sections.append("Here are the specific files I'm working with:\n")
            
            for file_path in request.selected_files:
                full_path = self.project_path / file_path
                if full_path.exists():
                    sections.append(f"### {file_path}")
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Detect file extension for syntax highlighting
                        ext = full_path.suffix.lower()
                        lang_map = {
                            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                            '.jsx': 'jsx', '.tsx': 'tsx', '.java': 'java', '.cpp': 'cpp',
                            '.c': 'c', '.h': 'c', '.cs': 'csharp', '.go': 'go',
                            '.rs': 'rust', '.php': 'php', '.rb': 'ruby', '.swift': 'swift',
                            '.kt': 'kotlin', '.scala': 'scala', '.r': 'r', '.sh': 'bash',
                            '.bat': 'batch', '.ps1': 'powershell', '.vue': 'vue',
                            '.html': 'html', '.css': 'css', '.scss': 'scss', '.sass': 'sass',
                            '.less': 'less', '.sql': 'sql', '.json': 'json', '.yaml': 'yaml',
                            '.yml': 'yaml', '.xml': 'xml', '.md': 'markdown'
                        }
                        lang = lang_map.get(ext, 'text')
                        
                        sections.append(f"```{lang}\n{content}\n```\n")
                    except Exception as e:
                        sections.append(f"*Error reading file: {e}*\n")
        
        # Task-specific details
        if hasattr(request, 'error_message') and request.error_message:
            sections.append("## Error Details")
            sections.append(f"**Error Message**: {request.error_message}")
        
        if hasattr(request, 'error_context') and request.error_context:
            sections.append(f"**When it occurs**: {request.error_context}")
        
        if hasattr(request, 'expected_behavior') and request.expected_behavior:
            sections.append(f"**Expected behavior**: {request.expected_behavior}")
            sections.append("")
        
        if hasattr(request, 'current_behavior') and request.current_behavior:
            sections.append("## Current vs Desired Behavior")
            sections.append(f"**Current**: {request.current_behavior}")
            
        if hasattr(request, 'desired_behavior') and request.desired_behavior:
            sections.append(f"**Desired**: {request.desired_behavior}")
            sections.append("")
        
        if hasattr(request, 'requirements') and request.requirements:
            sections.append("## Requirements")
            sections.append(f"{request.requirements}\n")
        
        if request.focus_area:
            sections.append("## Focus Area")
            sections.append(f"{request.focus_area}\n")
        
        # Task-specific request
        sections.append("## Request")
        sections.append(f"{template['focus']}")
        
        if request.task_type == 'add-feature':
            sections.append("Please provide:")
            sections.append("1. Implementation approach")
            sections.append("2. Required code changes")
            sections.append("3. Integration points with existing code")
        elif request.task_type == 'change-functionality':
            sections.append("Please provide:")
            sections.append("1. Analysis of current implementation")
            sections.append("2. Specific changes needed")
            sections.append("3. Potential impact on other components")
        elif request.task_type == 'explain-functionality':
            level = getattr(request, 'explanation_level', 'detailed')
            if level == 'high-level':
                sections.append("Please provide a high-level overview focusing on:")
                sections.append("1. Main purpose and responsibilities")
                sections.append("2. Key inputs and outputs")
                sections.append("3. How it fits into the larger system")
            elif level == 'step-by-step':
                sections.append("Please provide a step-by-step walkthrough including:")
                sections.append("1. Detailed execution flow")
                sections.append("2. Key decision points and logic")
                sections.append("3. Data transformations at each step")
            else:
                sections.append("Please provide a detailed explanation including:")
                sections.append("1. How the functionality works")
                sections.append("2. Key components and their roles")
                sections.append("3. Important implementation details")
        elif request.task_type == 'explain-architecture':
            audience = getattr(request, 'audience', 'developer')
            if audience == 'architect':
                sections.append("Please provide an architectural analysis including:")
                sections.append("1. Design patterns and architectural principles")
                sections.append("2. Component relationships and dependencies")
                sections.append("3. Scalability and maintainability considerations")
            elif audience == 'technical':
                sections.append("Please provide a technical overview including:")
                sections.append("1. High-level system design")
                sections.append("2. Key technologies and frameworks")
                sections.append("3. Data flow and integration points")
            else:
                sections.append("Please provide a developer-friendly explanation including:")
                sections.append("1. Overall structure and organization")
                sections.append("2. Main components and their purposes")
                sections.append("3. How to navigate and work with the project")
        elif request.task_type == 'debug-error':
            sections.append("Please provide:")
            sections.append("1. Analysis of the potential issue")
            sections.append("2. Specific code changes needed")
            sections.append("3. Explanation of why this fixes the problem")
            sections.append("4. Steps to test the fix")
        
        return "\n".join(sections)

class InteractiveCLI:
    """Interactive CLI interface for context building"""
    
    def __init__(self):
        self.builder = None
        self.request = None
        
    def run(self, project_path: str):
        """Run interactive CLI session"""
        print(f"\n🔧 Interactive Context Builder")
        print(f"📁 Project: {project_path}\n")
        
        self.builder = ContextBuilder(project_path)
        analysis = self.builder.analyzer.analyze()
        
        # Show project overview
        print(f"Found {len(analysis['source_files'])} source files")
        if analysis['main_modules']:
            print(f"Main modules: {', '.join(analysis['main_modules'])}")
        
        # Get task type
        task_type = self._get_task_type()
        
        # Get description
        description = input("\nDescribe what you want to do: ").strip()
        
        # Get focus area (optional)
        focus_area = input("Any specific focus area? (optional): ").strip()
        focus_area = focus_area if focus_area else None
        
        # Select files
        selected_files = self._select_files(analysis)
        
        
        # Build request
        self.request = ContextRequest(
            project_path=project_path,
            task_type=task_type,
            description=description,
            selected_files=selected_files,
            focus_area=focus_area
        )
        
        # Build and display context
        context = self.builder.build_context(self.request)
        
        print("\n" + "="*60)
        print("GENERATED CONTEXT (ready to copy/paste):")
        print("="*60)
        print(context)
        print("="*60)
        
        # Save option
        save = input("\nSave to file? (y/N): ").lower().startswith('y')
        if save:
            filename = input("Filename (default: context.md): ").strip() or "context.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(context)
            print(f"✅ Saved to {filename}")
    
    def _get_task_type(self) -> str:
        """Get task type from user"""
        print("\nWhat do you want to do?")
        print("1. Add a new feature")
        print("2. Change existing functionality")
        print("3. Explain how something works")
        print("4. Explain the overall architecture")
        print("5. Debug an error/issue")
        
        while True:
            choice = input("Choose (1-5): ").strip()
            if choice == '1':
                return 'add-feature'
            elif choice == '2':
                return 'change-functionality'
            elif choice == '3':
                return 'explain-functionality'
            elif choice == '4':
                return 'explain-architecture'
            elif choice == '5':
                return 'debug-error'
            else:
                print("Please enter 1, 2, 3, 4, or 5")
    
    def _select_files(self, analysis: Dict) -> List[str]:
        """Interactive file selection"""
        print(f"\nSelect files to include:")
        print("0. Include all source files")
        
        all_files = analysis['source_files']
        for i, file in enumerate(all_files, 1):
            print(f"{i}. {file}")
        
        while True:
            selection = input(f"\nEnter numbers (1-{len(all_files)}) separated by commas, or 0 for all: ").strip()
            
            if selection == '0':
                return all_files
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                if all(0 <= i < len(all_files) for i in indices):
                    return [all_files[i] for i in indices]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter valid numbers separated by commas.")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Interactive Context Builder"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        help="Path to project directory (optional)"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch Flask web interface"
    )
    
    args = parser.parse_args()
    
    if args.web:
        from context_web import launch_web_interface
        launch_web_interface(args.project_path)
    else:
        # CLI mode - get project path if not provided
        project_path = args.project_path
        if not project_path:
            project_path = input("Enter path to project: ").strip()
        
        if not os.path.exists(project_path):
            print(f"Error: Project path '{project_path}' does not exist")
            return
        
        cli = InteractiveCLI()
        cli.run(project_path)

if __name__ == "__main__":
    main()