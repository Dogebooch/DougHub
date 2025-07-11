import os
import requests
import base64
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

dougdraw_bp = Blueprint('dougdraw', __name__, template_folder='../templates')

UPLOAD_FOLDER = 'resources/uploads'

@dougdraw_bp.route('/dougdraw', methods=['GET'])
def dougdraw_home():
    return render_template('dougdraw.html')

@dougdraw_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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
        return {'filename': filename, 'url': url_for('dougdraw.uploaded_file', filename=filename)}

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
                edited_filename = f"{name}_cropped.png"
                cropped_path = os.path.join(UPLOAD_FOLDER, edited_filename)
                cropped.save(cropped_path, format="PNG")
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

@dougdraw_bp.route('/dougdraw/inpaint', methods=['POST'])
def inpaint_new():
    import requests
    import traceback
    try:
        # 1. Get form data
        prompt = request.form.get('prompt')
        image_file = request.files.get('image')
        mask_file = request.files.get('mask')
        if not prompt or not image_file or not mask_file:
            return jsonify({"error": "Missing prompt, image, or mask"}), 400

        # Save the mask file as mask.png for test_inpaint.py to find
        mask_filename = 'mask.png'
        mask_path = os.path.join(UPLOAD_FOLDER, mask_filename)
        # Save mask as PNG using PIL
        mask_image = Image.open(mask_file.stream)
        mask_image.save(mask_path, format='PNG')
        print(f"Saved mask to: {mask_path}")

        # Save the image file as image.png (or use the original filename)
        image_filename = 'image.png'
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        # Save image as PNG using PIL
        image_image = Image.open(image_file.stream)
        image_image.save(image_path, format='PNG')
        print(f"Saved image to: {image_path}")

        # Re-open files for upload
        with open(image_path, "rb") as img_f, open(mask_path, "rb") as mask_f:
            # 2. Upload image
            image_res = requests.post(
                "http://127.0.0.1:9090/api/v1/images/upload",
                files={"file": (image_filename, img_f, 'image/png')},
                params={"image_category": "general", "is_intermediate": "false"}
            )
            print("Image upload response:", image_res.status_code, image_res.text)
            image_json = image_res.json()
            if "image_name" not in image_json:
                return jsonify({"error": f"Image upload failed: {image_json}"}), 500
            image_name = image_json["image_name"]

            # 3. Upload mask
            mask_res = requests.post(
                "http://127.0.0.1:9090/api/v1/images/upload",
                files={"file": (mask_filename, mask_f, 'image/png')},
                params={"image_category": "mask", "is_intermediate": "false"}
            )
            print("Mask upload response:", mask_res.status_code, mask_res.text)
            mask_json = mask_res.json()
            if "image_name" not in mask_json:
                return jsonify({"error": f"Mask upload failed: {mask_json}"}), 500
            mask_name = mask_json["image_name"]

        # 4. Submit generation job (SDXL text-to-image minimal graph)
        payload = {
            "batch": {
                "graph": {
                    "nodes": {
                        "model_loader": {
                            "type": "sdxl_model_loader",
                            "id": "model_loader",
                            "model": {
                                "key": "sdxl:juggernautXL_v9"
                            }
                        },
                        "prompt": {
                            "type": "sdxl_compel_prompt",
                            "id": "prompt",
                            "prompt": prompt,
                            "negative_prompt": ""
                        },
                        "denoise": {
                            "type": "denoise_latents",
                            "id": "denoise",
                            "cfg_scale": 7,
                            "steps": 30,
                            "model": {"ref": "model_loader"},
                            "positive_conditioning": {"ref": "prompt"},
                            "negative_conditioning": {"ref": "prompt"}
                        },
                        "save": {
                            "type": "save_image",
                            "id": "save",
                            "images": {"ref": "denoise"}
                        }
                    }
                }
            }
        }
        print("Payload to InvokeAI:", payload)

        gen_res = requests.post(
            "http://127.0.0.1:9090/api/v1/queue/default/enqueue_batch",
            json=payload
        )

        # 5. Return raw response for now
        return jsonify(gen_res.json())

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Inpainting error: {str(e)}"}), 500
