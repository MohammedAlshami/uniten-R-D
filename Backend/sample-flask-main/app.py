from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import requests
import tempfile
import os
from urllib.parse import urlparse, unquote
import os
import re
import zipfile

model = YOLO(r"C:\Users\USER\Desktop\Work\Uniten\Prototype\Backend\best.pt")
app = Flask(__name__)

# Example of enabling CORS for all routes but only for GET and POST methods
CORS(app)

import pyrebase

# Firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyBLv1DiRB6egmpaoIKfjODXZF5fYheQKIM",
    "authDomain": "realtimedatabasetest-f226a.firebaseapp.com",
    "databaseURL": "https://realtimedatabasetest-f226a-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "realtimedatabasetest-f226a",
    "storageBucket": "realtimedatabasetest-f226a.appspot.com",
    "messagingSenderId": "348704796176",
    "appId": "1:348704796176:web:38994c5ab4d54b752ce495",
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

def upload_image(image_path):
    # Get the filename from the image path
    filename = image_path.split('/')[-1]
    
    # Path in storage where the image will be uploaded
    storage_path = f"images/{filename}"
    
    # Upload the file
    storage.child(storage_path).put(image_path)
    
    # Get the URL of the uploaded file
    url = storage.child(storage_path).get_url(None)
    return url

def get_highest_numbered_folder(base_path):
    # Pattern to match folders like 'test', 'test2', 'test3', etc.
    pattern = re.compile(r'^test(\d*)$')
    
    # Get all entries in the base path
    entries = os.listdir(base_path)
    
    # Filter and extract the numeric parts of the folder names
    max_num = -1
    folder_name = None
    for entry in entries:
        match = pattern.match(entry)
        if match:
            # Extract the numeric part, if any (considering 'test' as 'test0')
            num_part = match.group(1)
            num = int(num_part) if num_part else 0
            # Keep track of the folder with the highest number
            if num > max_num:
                max_num = num
                folder_name = entry

    if folder_name is None:
        return None  # No matching folder found
    else:
        return os.path.join(base_path, folder_name)
    
    
def zip_files(paths):
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_file_path = temp_file.name
    temp_file.close()  # Close the file so zipfile can handle it

    # Create a zip file at the temporary file path
    with zipfile.ZipFile(temp_file_path, 'w') as zipf:
        for path in paths:
            # Add each file to the zip file, handle directories and files
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, arcname=os.path.relpath(file_path, start=os.path.dirname(path)))
            else:
                zipf.write(path, arcname=os.path.basename(path))

    # Return the path to the temporary zip file
    return temp_file_path
@app.route('/endpoint', methods=['POST'])
def handle_url():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Parse the URL to get the path, unquote to decode any URL-encoded characters
    path = urlparse(url).path
    filename = os.path.basename(unquote(path))
    _, ext = os.path.splitext(filename)  # Extract the extension

    # Create a temporary file with the extracted extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
        # Download the content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        temp.write(response.content)
        # The temp.name includes the file extension now
   

    results = model.predict( temp.name, save=True, imgsz=320, conf=0.1, project="", name="test")
    print(results)

    filename = os.path.basename(temp.name)
    
    base_path = r"C:\Users\USER\Desktop\Work\Uniten\Prototype\runs\segment"
    highest_folder = get_highest_numbered_folder(base_path)
    image_path = rf"{highest_folder}\{filename}"
    
    zip_path = zip_files([image_path])
    
    output_url = upload_image(zip_path)
    return jsonify({"url": output_url}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)