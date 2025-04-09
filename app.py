from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import cv2
import numpy as np
from PIL import Image
import io
import base64
import uuid
from rembg import remove

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Color gradients
COLOR_GRADIENTS = {
    'red': [(255, 95, 109), (255, 195, 113)],  # #ff5f6d to #ffc371
    'blue': [(41, 128, 185), (109, 213, 250)],  # #2980b9 to #6dd5fa
    'black': [(35, 37, 38), (65, 67, 69)],  # #232526 to #414345
    'white': [(224, 224, 224), (255, 255, 255)],  # #e0e0e0 to #ffffff
    'cyan': [(0, 210, 255), (58, 123, 213)],  # #00d2ff to #3a7bd5
    'green': [(86, 171, 47), (168, 224, 99)],  # #56ab2f to #a8e063
    'purple': [(142, 45, 226), (74, 0, 224)],  # #8e2de2 to #4a00e0
    'pink': [(249, 83, 198), (185, 29, 115)],  # #f953c6 to #b91d73
    'maroon': [(142, 14, 0), (31, 28, 24)]  # #8e0e00 to #1f1c18
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    # Read image
    image_data = file.read()
    
    # Remove background
    result = remove(image_data)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(PROCESSED_FOLDER, filename)
    
    # Save processed image
    with open(output_path, 'wb') as f:
        f.write(result)
    
    return jsonify({
        'image_url': f"/static/processed/{filename}"
    })

@app.route('/change-background', methods=['POST'])
def change_background():
    data = request.json
    
    if not data or 'image_url' not in data or 'color' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    image_url = data['image_url']
    color = data['color']
    
    if color not in COLOR_GRADIENTS:
        return jsonify({'error': 'Invalid color'}), 400
    
    # Get image path from URL
    image_path = image_url.replace('/', os.sep).lstrip(os.sep)
    
    # Read image with alpha channel
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        return jsonify({'error': 'Could not read image'}), 500
    
    # Create gradient background
    height, width = img.shape[:2]
    gradient = create_gradient(width, height, COLOR_GRADIENTS[color])
    
    # Combine foreground and background
    result = combine_with_background(img, gradient)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(PROCESSED_FOLDER, filename)
    
    # Save result
    cv2.imwrite(output_path, result)
    
    return jsonify({
        'image_url': f"/static/processed/{filename}"
    })

def create_gradient(width, height, colors):
    """Create a gradient background"""
    start_color, end_color = colors
    
    # Create gradient
    gradient = np.zeros((height, width, 3), np.uint8)
    
    for i in range(height):
        ratio = i / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        gradient[i, :] = [b, g, r]  # OpenCV uses BGR
    
    return gradient

def combine_with_background(foreground, background):
    """Combine foreground with alpha channel and background"""
    # Split the foreground image into channels
    b, g, r, a = cv2.split(foreground)
    
    # Normalize alpha channel
    alpha = a / 255.0
    
    # Create a 3-channel foreground image
    foreground_rgb = cv2.merge([b, g, r])
    
    # Resize background to match foreground dimensions
    background = cv2.resize(background, (foreground.shape[1], foreground.shape[0]))
    
    # Blend foreground and background
    result = np.zeros_like(foreground_rgb)
    
    for c in range(3):
        result[:, :, c] = foreground_rgb[:, :, c] * alpha + background[:, :, c] * (1 - alpha)
    
    return result

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment or fallback to 5000
    app.run(host='0.0.0.0', port=port, debug=False)

