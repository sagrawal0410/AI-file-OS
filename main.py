from flask import Flask, request, render_template_string
import os
import logging
from vector_indexing import build_index, semantic_search, DOCUMENTS
from real_time_file_update import start_file_watcher
from config import WATCH_DIRECTORY
from sentence_transformers import SentenceTransformer
app=Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')
INDEX_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI-Native File Finder</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .chat-container { max-width: 600px; margin: auto; }
        .chat-box { border: 1px solid #ccc; padding: 10px; border-radius: 5px; }
        .prompt { margin-bottom: 20px; }
        .message { padding: 10px; border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px; }
        .file-link { text-decoration: none; color: blue; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>AI-Native File Finder</h2>
        <form method="POST">
            <div class="prompt">
                <input type="text" name="query" placeholder="Enter your query here..." style="width:80%;" required>
                <button type="submit">Search</button>
            </div>
        </form>
        {% if results %}
            <div class="chat-box">
                {% for res in results %}
                    <div class="message">
                        <strong>File:</strong> {{ res.path }}<br>
                        <strong>Score:</strong> {{ res.score | round(2) }}<br>
                        <p>{{ res.snippet }}</p>
                        <a class="file-link" href="/file?path={{ res.path | urlencode }}">View Full File</a>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

FILE_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Content</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: auto; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>File: {{ path }}</h2>
        <pre>{{ content }}</pre>
        <a href="/">Back to Search</a>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        query = request.form.get('query')
        results = semantic_search(query, model)
    return render_template_string(INDEX_PAGE, results=results)

@app.route('/file')
def view_file():
    # For security, ensure the file is within the allowed directory
    path = request.args.get('path')
    if not path.startswith(WATCH_DIRECTORY):
        return "Unauthorized file access", 403

    file_content = ""
    for doc in DOCUMENTS:
        if doc['path'] == path:
            file_content = doc.get('text', '')
            break
    if not file_content:
        try:
            with open(path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            file_content = f"Error reading file: {e}"
    return render_template_string(FILE_PAGE, path=path, content=file_content)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Build the initial index before starting the UI.
    build_index(WATCH_DIRECTORY)
    # Start the file watcher (runs in its own thread)
    observer = start_file_watcher(WATCH_DIRECTORY)
    try:
        app.run(debug=True, port=5000)
    finally:
        observer.stop()
        observer.join()