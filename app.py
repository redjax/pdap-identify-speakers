import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import urllib.request
import sys
sys.path.append('./aws-transcribe-transcript/')
from transcript import main as transcribe

app = Flask(__name__)

# CSRF protection
SECRET_KEY = os.urandom(32)
# Directory for uploads
UPLOAD_FOLDER = './uploads/unprocessed'
# Directory for processed files
PROCESSED_FOLDER = './uploads/processed'
# Allowed filetypes
ALLOWED_EXTENSIONS = {'json'}

# Add CSRF to app
app.config['SECRET_KEY'] = SECRET_KEY
# Set upload folder for app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set processed folder for transcription outputs
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER


def allowed_file(filename):
    """Check if uploaded file is accepted type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_file(filename):
    """Run the uploaded file through aws-transcribe-transcript.py."""
    transcription_output = transcribe(filename)
    transcription_output.save(os.path.join(app.config['OUTPUT_FOLDER'], transcription_output))


@app.route('/')
def upload_form():
    """Show the upload form."""
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    """Allow file(s) to be uploaded, run checks, and save to server."""
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        for file in files:
            # If file matches allowed filetypes
            if file and allowed_file(file.filename):
                # Clean file's name before saving
                filename = secure_filename(file.filename)
                # Save file to upload folder
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File(s) successfully uploaded')
            process_file(file)
            return redirect('/')
        

# Run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)