# Import libraries
import os
from flask import Flask, render_template, request, make_response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
import pandas as pd
from script import get_URLs, namescrape, print_input, convert

# Create an app instance
app = Flask(__name__)
dropzone = Dropzone(app)

# Update app configuration
app.config.update (
    UPLOAD_FOLDER = '.\\uploads',
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM = True,
    DROPZONE_ALLOWED_FILE_TYPE='.csv',
    DROPZONE_MAX_FILES=1,
    DROPZONE_REDIRECT_VIEW= "download"
)

# Main page
@app.route("/", methods =['GET', 'POST'])
def index():
    if request.method == 'POST':
        #Take CSV input
        filename = 'quotes.csv'
        input_file = request.files.get('file')
        input_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Return template
    return render_template('index.html')

@app.route("/download")
def download():
    # Initialize empty variables for Jinja
    table = ''
    total = ''
    
    # Read Uploaded data
    input_data = pd.read_csv(r'.\uploads\quotes.csv')
    
    # Get URLs for scraping
    get_URLs_list = get_URLs(input_data)
    urls = get_URLs_list[0]
    urls2 = get_URLs_list[1]
    
    # Get Name Data
    names = namescrape(urls)
    
    # Get data from upload
    userdata = print_input(input_data, names)
    # Store variables
    table = userdata[0]
    total = userdata[1]
    etfnames = userdata[2]
    pf = userdata[3]
    pft = userdata[4]
    
    # Convert CSV and download result
    output_data = convert(urls2, pf, pft, etfnames)
    output = output_data.to_csv(r'.\uploads\result.csv', index=False)
    
    return render_template('download.html', table=table, total = total, filename='result.csv')

# Download result route
@app.route("/output/<filename>")
def output(filename):
    return send_from_directory('uploads', filename, as_attachment=True)

# On running server.py, run Flask app
if __name__ == "__main__":
    app.run(debug=True)
