from flask import Flask, request, render_template
import easyocr
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import os
import tempfile

app = Flask(__name__)

# Initialize the EasyOCR Reader
reader = easyocr.Reader(['en'])

def extract_text(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    extracted_lines = []

    if file_extension == '.pdf':
        pages = convert_from_path(file_path)
        for page in pages:
            page_np = np.array(page)
            page_text = reader.readtext(page_np, detail=0)
            extracted_lines.extend(page_text)

    elif file_extension in ['.png', '.jpg', '.jpeg']:
        image = Image.open(file_path)
        image_np = np.array(image)
        extracted_lines = reader.readtext(image_np, detail=0)

    else:
        raise ValueError("Unsupported file format. Please use PDF, PNG, or JPEG.")
    
    return extracted_lines

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")
        if file:
            # Create a temporary file to save the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            try:
                extracted_text = extract_text(temp_file_path)
                result = '\n'.join(extracted_text)
                
                # Remove the temporary file
                os.unlink(temp_file_path)
                
                return render_template('index.html', result=result)
            except Exception as e:
                # Remove the temporary file in case of an error
                os.unlink(temp_file_path)
                return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
