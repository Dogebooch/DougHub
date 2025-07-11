import os
import requests
import base64
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

dougdraw_bp = Blueprint('dougdraw', __name__, template_folder='../templates')

UPLOAD_FOLDER = 'resources/uploads'

@dougdraw_bp.route('/dougdraw', methods=['GET'])
def dougdraw_home():
    return render_template('dougdraw.html')

@dougdraw_bp.route('/dougdraw/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No file uploaded', 400

    file = request.files['image']
    if not file or not file.filename:
        return 'No file selected', 400

    filename = secure_filename(str(file.filename))
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # If the upload is triggered via AJAX (fetch/XHR), return JSON.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'filename': filename, 'url': url_for('static', filename=f'uploads/{filename}')}

    # Otherwise, render the template as before.
    return render_template('dougdraw.html', filename=filename)

@dougdraw_bp.route('/dougdraw/edit', methods=['POST'])
def edit_image():
    filename = request.form.get('filename')
    prompt = request.form.get('prompt')
    x = request.form.get('x')
    y = request.form.get('y')
    width = request.form.get('width')
    height = request.form.get('height')

    edited_filename = None
    if filename and x and y and width and height:
        try:
            x = int(x)
            y = int(y)
            width = int(width)
            height = int(height)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            with Image.open(image_path) as img:
                cropped = img.crop((x, y, x + width, y + height))
                name, ext = os.path.splitext(filename)
                edited_filename = f"{name}_cropped{ext}"
                cropped_path = os.path.join(UPLOAD_FOLDER, edited_filename)
                cropped.save(cropped_path)
        except Exception as e:
            print(f"Error cropping image: {e}")
            edited_filename = None

    return render_template('dougdraw.html', filename=filename, prompt=prompt, edited_filename=edited_filename)

@dougdraw_bp.route('/inpaint', methods=['POST'])
def inpaint():
    # Get form data
    prompt = request.form.get('prompt')
    image_file = request.files.get('image')
    if not prompt or not image_file:
        return jsonify({'error': 'Missing prompt or image'}), 400

    # Load the image
    image = Image.open(image_file.stream).convert("RGB")

    # Convert image to base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Build payload for InvokeAI's REST API
    payload = {
        "prompt": prompt,
        "init_image": base64_image,
        "denoising_strength": 0.75,
        "model": "Dreamshaper 8",
        "image_mode": "IMAGE2IMAGE",
        "scheduler": "DPM++_2M_Karras",
        "cfg_scale": 6.5,
        "steps": 28,
        "width": image.width,
        "height": image.height
    }

    # Send request to InvokeAI server
    try:
        print(f"Sending request to InvokeAI with payload: {payload.keys()}")
        response = requests.post("http://127.0.0.1:9090/api/v1/generate/image2image", json=payload)
        
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return jsonify({'error': 'InvokeAI failed', 'details': response.text}), 500

        # Extract image from response
        result = response.json()
        print(f"Response keys: {result.keys()}")
        output_b64 = result["images"][0]["image"]

        return jsonify({"image": output_b64})
        
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to InvokeAI server. Make sure it's running on localhost:9090"}), 500
    except Exception as e:
        print(f"Exception during inpainting: {str(e)}")
        return jsonify({"error": f"Inpainting error: {str(e)}"}), 500
