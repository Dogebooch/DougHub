import requests
import os
import glob
from PIL import Image

# Find the first image and mask files in resources/uploads/
upload_dir = "resources/uploads"
image_files = glob.glob(os.path.join(upload_dir, "*.png")) + glob.glob(os.path.join(upload_dir, "*.jpg")) + glob.glob(os.path.join(upload_dir, "*.jpeg"))
mask_files = glob.glob(os.path.join(upload_dir, "*mask*.png")) + glob.glob(os.path.join(upload_dir, "*mask*.jpg"))

if not image_files:
    print("No image files found in resources/uploads/")
    print("Please upload an image via the web interface first.")
    exit(1)

if not mask_files:
    print("No mask files found in resources/uploads/")
    print("Please create a mask file with 'mask' in the filename.")
    exit(1)

# Use the first available image and mask
image_path = image_files[0]
mask_path = mask_files[0]

print(f"Using image: {image_path}")
print(f"Using mask: {mask_path}")

# Save uploaded file as PNG using PIL
image_file = open(image_path, "rb")
image = Image.open(image_file)
image_path_png = os.path.join(upload_dir, 'image.png')
image.save(image_path_png, format='PNG')

# Re-open for upload
with open(image_path_png, 'rb') as img_f:
    image_res = requests.post(
        "http://127.0.0.1:9090/api/v1/images/upload",
        files={"file": ('image.png', img_f, 'image/png')},
        params={"image_category": "general", "is_intermediate": "false"}
    )

# Save uploaded file as PNG using PIL
mask_file = open(mask_path, "rb")
mask = Image.open(mask_file)
mask_path_png = os.path.join(upload_dir, 'mask.png')
mask.save(mask_path_png, format='PNG')

# Re-open for upload
with open(mask_path_png, 'rb') as mask_f:
    mask_res = requests.post(
        "http://127.0.0.1:9090/api/v1/images/upload",
        files={"file": ('mask.png', mask_f, 'image/png')},
        params={"image_category": "mask", "is_intermediate": "false"}
    )


files = {
    "image": open(image_path_png, "rb"),
    "mask": open(mask_path_png, "rb")
}

data = {
    "prompt": "add a hammer to the left hand"
}

res = requests.post("http://127.0.0.1:5000/dougdraw/inpaint", data=data, files=files)

print("Status:", res.status_code)
print("Response:", res.json()) 