from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import threading
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure static folder
STATIC_FOLDER = 'static'
app.static_folder = STATIC_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'srt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .srt files are allowed'}), 400
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    # Get translation options
    method = request.form.get('method', 'local')
    batch_size = request.form.get('batch_size', 32, type=int)
    preserve_names = request.form.get('preserve_names', 'true') == 'true'
    movie_context = request.form.get('movie_context', '')
    
    # Build output path
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_vn{ext}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Prepare command based on selected method
    cmd = []
    if method == 'local':
        cmd = [
            'python', 'local_translation.py',
            input_path,
            '-o', output_path,
            '--batch-size', str(batch_size)
        ]
        if not preserve_names:
            cmd.append('--no-preserve-names')
    elif method == 'hybrid':
        cmd = [
            'python', 'hybrid_translator.py',
            input_path,
            '-o', output_path,
            '--batch-size', str(batch_size)
        ]
        if 'openrouter_api_key' in request.form:
            cmd.extend(['--openrouter-api-key', request.form['openrouter_api_key']])
        if not preserve_names:
            cmd.append('--no-gemini')  # This is a simplification, actual implementation would be different
        if movie_context:
            cmd.extend(['--movie-context', movie_context])
    else:  # gemini
        cmd = [
            'python', 'srt_translator.py',
            input_path,
            '-o', output_path,
            '--batch-size', str(batch_size)
        ]
        if not preserve_names:
            cmd.append('--no-preserve-names')
    
    try:
        # Run translation command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode != 0:
            return jsonify({'error': f'Translation failed: {result.stderr}'}), 500
        
        # Return download link
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'message': 'Translation completed successfully'
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Translation timed out'}), 500
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "File not found", 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
