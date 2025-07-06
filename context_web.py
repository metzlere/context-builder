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

def create_templates():
    """Create template files"""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Create main HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Context Builder</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 100px; resize: vertical; }
        button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        button:hover { background-color: #0056b3; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }
        .file-list { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9; }
        .file-item { margin-bottom: 5px; }
        .file-item input { width: auto; margin-right: 10px; }
        .context-output { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 4px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px; }
        .error { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; }
        .success { color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 4px; }
        .loading { text-align: center; padding: 20px; }
        .copy-btn { background-color: #28a745; }
        .copy-btn:hover { background-color: #218838; }
        .tabs { display: flex; border-bottom: 1px solid #ddd; margin-bottom: 20px; }
        .tab { padding: 10px 20px; cursor: pointer; border: none; background: #f8f9fa; color: #333; margin-right: 5px; border-radius: 4px 4px 0 0; }
        .tab.active { background-color: #007bff; color: white; }
        .tab:hover { background-color: #e9ecef; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Interactive Context Builder</h1>
            <p>Build optimized contexts for LLM interactions</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('setup')">Setup</button>
            <button class="tab" onclick="showTab('task')">Task Configuration</button>
            <button class="tab" onclick="showTab('context')">Generate Context</button>
        </div>

        <!-- Setup Tab -->
        <div id="setup" class="tab-content active">
            <div class="section">
                <h2>Project Setup</h2>
                <div class="form-group">
                    <label for="project-path">Project Path:</label>
                    <input type="text" id="project-path" placeholder="Enter path to your project">
                </div>
                <button onclick="analyzeProject()">Analyze Project</button>
                <p><small>This will scan your project for source files, tests, configs, and build a directory structure.</small></p>
            </div>

            <div id="project-info" class="section" style="display: none;">
                <h2>Project Information</h2>
                <div id="project-details"></div>
            </div>
        </div>

        <!-- Task Configuration Tab -->
        <div id="task" class="tab-content">
            <div class="section">
                <h2>Select Files</h2>
                <div id="file-list" class="file-list">
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="select-all" onchange="toggleAllFiles()">
                            Select All Source Files
                        </label>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Task Configuration</h2>
                <div class="form-group">
                    <label for="task-type">What do you want to do?</label>
                    <select id="task-type" onchange="updateTaskFields()">
                        <option value="">Select a task...</option>
                        <option value="add-feature">Add a new feature</option>
                        <option value="change-functionality">Change existing functionality</option>
                        <option value="explain-functionality">Explain how something works</option>
                        <option value="explain-architecture">Explain the overall architecture</option>
                        <option value="debug-error">Debug an error/issue</option>
                    </select>
                </div>
                
                <!-- Dynamic task-specific fields -->
                <div id="task-fields"></div>
            </div>
        </div>

        <!-- Context Tab -->
        <div id="context" class="tab-content">
            <div class="section">
                <h2>Generated Context</h2>
                <button onclick="buildContext()">Generate Context</button>
                <button class="copy-btn" onclick="copyContext()">Copy to Clipboard</button>
                <div id="context-output" class="context-output"></div>
            </div>
        </div>

        <div id="messages"></div>
    </div>

    <script>
        let currentAnalysis = null;

        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.getAttribute('onclick') === `showTab('${tabName}')`) {
                    tab.classList.add('active');
                }
            });
        }

        function showMessage(message, type = 'info') {
            const messagesDiv = document.getElementById('messages');
            const messageClass = type === 'error' ? 'error' : 'success';
            messagesDiv.innerHTML = `<div class="${messageClass}">${message}</div>`;
            setTimeout(() => messagesDiv.innerHTML = '', 5000);
        }

        async function analyzeProject() {
            const projectPath = document.getElementById('project-path').value;
            if (!projectPath) {
                showMessage('Please enter a project path', 'error');
                return;
            }

            showMessage('Analyzing project...', 'info');

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({project_path: projectPath})
                });

                const data = await response.json();
                
                if (data.success) {
                    currentAnalysis = data.analysis;
                    displayProjectInfo(data.analysis);
                    populateFileList(data.analysis);
                    showMessage('Project analyzed successfully!', 'success');
                    
                    // Auto-advance to Task Configuration tab after 2 seconds
                    setTimeout(function() {
                        showTab('task');
                    }, 2000);
                } else {
                    showMessage(data.error, 'error');
                }
            } catch (error) {
                showMessage('Error analyzing project: ' + error.message, 'error');
            }
        }

        function displayProjectInfo(analysis) {
            const projectDetails = document.getElementById('project-details');
            projectDetails.innerHTML = `
                <p><strong>Project:</strong> ${analysis.project_name}</p>
                <p><strong>Source Files:</strong> ${analysis.source_files.length}</p>
                <p><strong>Test Files:</strong> ${analysis.test_files.length}</p>
                <p><strong>Config Files:</strong> ${analysis.config_files.length}</p>
                ${analysis.main_modules.length > 0 ? `<p><strong>Main Modules:</strong> ${analysis.main_modules.join(', ')}</p>` : ''}
                <details>
                    <summary>Project Structure</summary>
                    <pre>${analysis.structure}</pre>
                </details>
            `;
            document.getElementById('project-info').style.display = 'block';
        }

        function populateFileList(analysis) {
            const fileList = document.getElementById('file-list');
            
            // Clear existing content but keep the select all checkbox
            const selectAllDiv = fileList.querySelector('.form-group');
            fileList.innerHTML = '';
            fileList.appendChild(selectAllDiv);

            analysis.source_files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <label>
                        <input type="checkbox" value="${file}" class="file-checkbox">
                        ${file}
                    </label>
                `;
                fileList.appendChild(fileItem);
            });
        }

        function updateTaskFields() {
            const taskType = document.getElementById('task-type').value;
            const taskFields = document.getElementById('task-fields');
            
            let fieldsHtml = '';
            
            switch(taskType) {
                case 'add-feature':
                    fieldsHtml = `
                        <div class="form-group">
                            <label for="feature-description">Describe the feature you want to add:</label>
                            <textarea id="feature-description" placeholder="E.g., 'Add user authentication with email/password login'"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="requirements">Any specific requirements?</label>
                            <textarea id="requirements" placeholder="E.g., 'Should integrate with existing user management system'"></textarea>
                        </div>
                    `;
                    break;
                    
                case 'change-functionality':
                    fieldsHtml = `
                        <div class="form-group">
                            <label for="current-behavior">What currently happens?</label>
                            <textarea id="current-behavior" placeholder="Describe the current behavior"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="desired-behavior">What should happen instead?</label>
                            <textarea id="desired-behavior" placeholder="Describe the desired behavior"></textarea>
                        </div>
                    `;
                    break;
                    
                case 'explain-functionality':
                    fieldsHtml = `
                        <div class="form-group">
                            <label for="functionality-focus">What specific functionality do you want explained?</label>
                            <input type="text" id="functionality-focus" placeholder="E.g., 'user authentication flow' or 'data processing pipeline'">
                        </div>
                        <div class="form-group">
                            <label for="explanation-level">Level of detail:</label>
                            <select id="explanation-level">
                                <option value="high-level">High-level overview</option>
                                <option value="detailed">Detailed explanation</option>
                                <option value="step-by-step">Step-by-step walkthrough</option>
                            </select>
                        </div>
                    `;
                    break;
                    
                case 'explain-architecture':
                    fieldsHtml = `
                        <div class="form-group">
                            <label for="architecture-focus">Any specific architectural aspects to focus on?</label>
                            <input type="text" id="architecture-focus" placeholder="E.g., 'data flow', 'component relationships', 'design patterns'">
                        </div>
                        <div class="form-group">
                            <label for="audience">Who is this explanation for?</label>
                            <select id="audience">
                                <option value="developer">New developer joining the project</option>
                                <option value="technical">Technical stakeholder</option>
                                <option value="architect">Solution architect</option>
                            </select>
                        </div>
                    `;
                    break;
                    
                case 'debug-error':
                    fieldsHtml = `
                        <div class="form-group">
                            <label for="error-message">Error message (if any):</label>
                            <textarea id="error-message" placeholder="Paste the error message here"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="error-context">When does this error occur?</label>
                            <textarea id="error-context" placeholder="Describe the steps that lead to the error"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="expected-behavior">What should happen instead?</label>
                            <textarea id="expected-behavior" placeholder="Describe the expected behavior"></textarea>
                        </div>
                    `;
                    break;
                    
                default:
                    fieldsHtml = '';
            }
            
            taskFields.innerHTML = fieldsHtml;
        }

        function toggleAllFiles() {
            const selectAll = document.getElementById('select-all');
            const checkboxes = document.querySelectorAll('.file-checkbox');
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAll.checked;
            });
        }

        function getSelectedFiles() {
            const checkboxes = document.querySelectorAll('.file-checkbox:checked');
            return Array.from(checkboxes).map(cb => cb.value);
        }

        async function buildContext() {
            if (!currentAnalysis) {
                showMessage('Please analyze a project first', 'error');
                return;
            }

            const selectedFiles = getSelectedFiles();
            if (selectedFiles.length === 0) {
                showMessage('Please select at least one file', 'error');
                return;
            }

            const taskType = document.getElementById('task-type').value;
            if (!taskType) {
                showMessage('Please select a task type', 'error');
                return;
            }

            // Collect task-specific data
            let taskData = { task_type: taskType };
            
            switch(taskType) {
                case 'add-feature':
                    const featureDesc = document.getElementById('feature-description').value;
                    const requirements = document.getElementById('requirements').value;
                    if (!featureDesc) {
                        showMessage('Please describe the feature you want to add', 'error');
                        return;
                    }
                    taskData.description = featureDesc;
                    taskData.requirements = requirements;
                    break;
                    
                case 'change-functionality':
                    const currentBehavior = document.getElementById('current-behavior').value;
                    const desiredBehavior = document.getElementById('desired-behavior').value;
                    if (!currentBehavior || !desiredBehavior) {
                        showMessage('Please describe both current and desired behavior', 'error');
                        return;
                    }
                    taskData.description = `Change functionality: ${currentBehavior} → ${desiredBehavior}`;
                    taskData.current_behavior = currentBehavior;
                    taskData.desired_behavior = desiredBehavior;
                    break;
                    
                case 'explain-functionality':
                    const functionalityFocus = document.getElementById('functionality-focus').value;
                    const explanationLevel = document.getElementById('explanation-level').value;
                    if (!functionalityFocus) {
                        showMessage('Please specify what functionality to explain', 'error');
                        return;
                    }
                    taskData.description = `Explain functionality: ${functionalityFocus}`;
                    taskData.focus_area = functionalityFocus;
                    taskData.explanation_level = explanationLevel;
                    break;
                    
                case 'explain-architecture':
                    const architectureFocus = document.getElementById('architecture-focus').value;
                    const audience = document.getElementById('audience').value;
                    taskData.description = 'Explain the overall architecture';
                    taskData.focus_area = architectureFocus;
                    taskData.audience = audience;
                    break;
                    
                case 'debug-error':
                    const errorMessage = document.getElementById('error-message').value;
                    const errorContext = document.getElementById('error-context').value;
                    const expectedBehavior = document.getElementById('expected-behavior').value;
                    if (!errorContext) {
                        showMessage('Please describe when the error occurs', 'error');
                        return;
                    }
                    taskData.description = 'Debug an error/issue';
                    taskData.error_message = errorMessage;
                    taskData.error_context = errorContext;
                    taskData.expected_behavior = expectedBehavior;
                    break;
            }

            const contextData = {
                ...taskData,
                selected_files: selectedFiles
            };

            showMessage('Building context...', 'info');

            try {
                const response = await fetch('/api/build-context', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(contextData)
                });

                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('context-output').textContent = data.context;
                    showMessage('Context generated successfully!', 'success');
                } else {
                    showMessage(data.error, 'error');
                }
            } catch (error) {
                showMessage('Error building context: ' + error.message, 'error');
            }
        }

        async function copyContext() {
            const contextOutput = document.getElementById('context-output');
            if (!contextOutput.textContent) {
                showMessage('No context to copy', 'error');
                return;
            }

            try {
                await navigator.clipboard.writeText(contextOutput.textContent);
                showMessage('Context copied to clipboard!', 'success');
            } catch (error) {
                showMessage('Failed to copy to clipboard', 'error');
            }
        }
    </script>
</body>
</html>'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

def launch_web_interface(project_path: str = None):
    """Launch the Flask web interface"""
    global current_project
    current_project = project_path
    
    # Create templates if they don't exist
    create_templates()
    
    if project_path:
        print(f"🌐 Launching web interface for: {project_path}")
    else:
        print("🌐 Launching web interface - select project in browser")
    print("🔗 Open your browser to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # For testing
    launch_web_interface(".")