from flask import Flask, request, render_template, redirect, url_for,session
from werkzeug.utils import secure_filename
import os
import pyresume

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = '/Users/pranavaggarwal/Documents/upload'
results = None
address=""

@app.route('/')
def index():
    session['processed'] = False
    return render_template('index.html')

@app.route('/process')
def process_file_background():
    global results
    global address
    resume,time=pyresume.master(pyresume.extract_text(address,pyresume.determine_file_type(address)))
    html= pyresume.generate_html(resume,time)
    with open("/Users/pranavaggarwal/Documents/Personal Website/app/templates/results.html", "w") as f:
        f.write(html)
    resume.clear()
    results = get_results()
    session['processed'] = True
    return None

@app.route('/upload', methods=['POST'])
def upload():
    global address
    file = request.files['file']
    if file:
        # Delete the previous file
        previous_file = os.path.join(app.config['UPLOAD_FOLDER'], "resume.pdf")
        if os.path.exists(previous_file):
            os.remove(previous_file)
        # Save the new file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        address=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return redirect(url_for('wait'))

    return 'No file selected'

@app.route('/wait')
def wait():
    return render_template('wait.html')

def get_results():
    # code to get results here
    return 'Results'

@app.route('/results')
def display_results():
    if not session.get('processed'):
        return redirect(url_for('index'))
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=False)
