"""
Flask Web Interface for Context Builder
Provides a user-friendly web GUI for building LLM contexts
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from pathlib import Path
from context_builder import ContextBuilder, ContextRequest, ProjectAnalyzer

app = Flask(__name__)

# Global state
current_project = None
current_builder = None

@app.route('/')
def index():
    """Main interface"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    """Analyze the current project"""
    global current_project, current_builder
    
    try:
        data = request.json
        project_path = data.get('project_path', current_project)
        
        if not project_path or not os.path.exists(project_path):
            return jsonify({'error': 'Invalid project path'}), 400
        
        current_project = project_path
        current_builder = ContextBuilder(project_path)
        
        analysis = current_builder.analyzer.analyze()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/build-context', methods=['POST'])
def build_context():
    """Build context based on user selections"""
    global current_builder
    
    if not current_builder:
        return jsonify({'error': 'No project loaded'}), 400
    
    try:
        data = request.json
        
        # Create context request
        context_request = ContextRequest(
            project_path=current_project,
            task_type=data['task_type'],
            description=data['description'],
            selected_files=data['selected_files'],
            focus_area=data.get('focus_area'),
            requirements=data.get('requirements'),
            current_behavior=data.get('current_behavior'),
            desired_behavior=data.get('desired_behavior'),
            explanation_level=data.get('explanation_level'),
            audience=data.get('audience'),
            error_message=data.get('error_message'),
            error_context=data.get('error_context'),
            expected_behavior=data.get('expected_behavior')
        )
        
        # Build context
        context = current_builder.build_context(context_request)
        
        return jsonify({
            'success': True,
            'context': context
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file-content/<path:filename>')
def get_file_content(filename):
    """Get content of a specific file for preview"""
    global current_project
    
    if not current_project:
        return jsonify({'error': 'No project loaded'}), 400
    
    try:
        file_path = Path(current_project) / filename
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def launch_web_interface(project_path: str = None):
    """Launch the Flask web interface"""
    global current_project
    current_project = project_path
    
    if project_path:
        print(f"🌐 Launching web interface for: {project_path}")
    else:
        print("🌐 Launching web interface - select project in browser")
    print("🔗 Open your browser to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # For testing
    launch_web_interface(".")