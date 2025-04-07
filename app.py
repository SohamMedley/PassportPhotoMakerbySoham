from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import secrets
import cv2
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import uuid
import requests
from rembg import remove

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory database for demo purposes
# In a real application, you would use a proper database like SQLite, PostgreSQL, etc.
users_db = {}
photos_db = {}
otp_db = {}

# Helper function to remove background using rembg library
def remove_background(image_path):
    try:
        # Read the input image
        with open(image_path, 'rb') as f:
            img_data = f.read()
        
        # Remove background using rembg (which uses U2Net model)
        output_data = remove(img_data)
        
        # Save the output image
        output_path = image_path.replace('.jpg', '_transparent.png').replace('.jpeg', '_transparent.png').replace('.png', '_transparent.png')
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        return output_path
    except Exception as e:
        print(f"Error in remove_background: {str(e)}")
        # Fallback to advanced OpenCV method if rembg fails
        return remove_background_opencv(image_path)

# Fallback method using advanced OpenCV techniques
def remove_background_opencv(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to RGB (OpenCV uses BGR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Create a copy for the result
    result = img.copy()
    
    # Convert to different color spaces for better segmentation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    
    # Create masks for skin detection in different color spaces
    # HSV skin detection
    lower_skin_hsv = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin_hsv = np.array([20, 255, 255], dtype=np.uint8)
    mask_hsv = cv2.inRange(hsv, lower_skin_hsv, upper_skin_hsv)
    
    # YCrCb skin detection
    lower_skin_ycrcb = np.array([0, 135, 85], dtype=np.uint8)
    upper_skin_ycrcb = np.array([255, 180, 135], dtype=np.uint8)
    mask_ycrcb = cv2.inRange(ycrcb, lower_skin_ycrcb, upper_skin_ycrcb)
    
    # Combine masks
    mask_skin = cv2.bitwise_or(mask_hsv, mask_ycrcb)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Combine with skin detection
    mask_combined = cv2.bitwise_or(thresh, mask_skin)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask_morphed = cv2.morphologyEx(mask_combined, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask_morphed = cv2.morphologyEx(mask_morphed, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Dilate to expand the mask
    mask_dilated = cv2.dilate(mask_morphed, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create mask for the largest contour (assuming it's the person)
    mask_person = np.zeros_like(gray)
    
    if contours:
        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Draw filled contour on mask
        cv2.drawContours(mask_person, [largest_contour], 0, 255, -1)
        
        # Apply additional morphological operations to refine mask
        mask_person = cv2.morphologyEx(mask_person, cv2.MORPH_CLOSE, kernel, iterations=5)
    
    # Apply GrabCut for better segmentation
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    
    # Use the mask to initialize GrabCut
    mask_grabcut = np.zeros(img.shape[:2], np.uint8)
    mask_grabcut[mask_person == 255] = cv2.GC_PR_FGD  # Probable foreground
    mask_grabcut[mask_person == 0] = cv2.GC_BGD  # Background
    
    # Apply GrabCut
    rect = cv2.boundingRect(mask_person)
    try:
        cv2.grabCut(img, mask_grabcut, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
    except:
        # If GrabCut fails, use the original mask
        mask_final = mask_person
    else:
        # Create final mask
        mask_final = np.where((mask_grabcut == cv2.GC_PR_FGD) | (mask_grabcut == cv2.GC_FGD), 255, 0).astype('uint8')
    
    # Create transparent background
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = mask_final
    
    # Save the image with transparent background
    output_path = image_path.replace('.jpg', '_transparent.png').replace('.jpeg', '_transparent.png').replace('.png', '_transparent.png')
    cv2.imwrite(output_path, rgba)
    
    return output_path

# Helper function to send OTP email (simulated for demo)
def send_otp_email(email, otp):
    # In a real application, you would use an email service like SendGrid, Mailgun, etc.
    # For demo purposes, we'll just print the OTP
    print(f"Sending OTP {otp} to {email}")
    return True

# Generate a random 6-digit OTP
def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_photo():
    if 'photo' not in request.files:
        flash('No photo uploaded')
        return redirect(url_for('index'))
    
    photo = request.files['photo']
    
    if photo.filename == '':
        flash('No photo selected')
        return redirect(url_for('index'))
    
    # Save the uploaded photo
    filename = str(uuid.uuid4()) + os.path.splitext(photo.filename)[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(filepath)
    
    # Process the photo (remove background)
    try:
        processed_path = remove_background(filepath)
        
        # Store the processed photo path in session
        session['processed_photo'] = processed_path
        
        # Redirect to edit page
        return redirect(url_for('edit'))
    except Exception as e:
        flash(f'Error processing photo: {str(e)}')
        return redirect(url_for('index'))

@app.route('/edit')
def edit():
    if 'processed_photo' not in session:
        flash('No photo to edit')
        return redirect(url_for('index'))
    
    # Get the processed photo path
    photo_path = session['processed_photo']
    
    # Convert to URL
    photo_url = '/' + photo_path
    
    # Mock user data for template
    user = None
    if 'user' in session:
        user_id = session['user']
        user = users_db.get(user_id)
    
    return render_template('edit.html', photo_url=photo_url, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        otp = request.form.get('otp')
        
        # Validate email
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address')
            return redirect(url_for('login'))
        
        # Check if OTP is provided
        if not otp:
            # Generate and send OTP
            new_otp = generate_otp()
            otp_db[email] = {
                'otp': new_otp,
                'expires': datetime.now() + timedelta(minutes=10)
            }
            send_otp_email(email, new_otp)
            flash(f'OTP sent to {email}')
            return render_template('login.html', email=email, show_otp=True)
        
        # Verify OTP
        if email not in otp_db or otp_db[email]['otp'] != otp:
            flash('Invalid OTP')
            return redirect(url_for('login'))
        
        # Check if OTP is expired
        if datetime.now() > otp_db[email]['expires']:
            flash('OTP expired')
            return redirect(url_for('login'))
        
        # Check if user exists
        user_id = None
        for uid, user in users_db.items():
            if user['email'] == email:
                user_id = uid
                break
        
        if not user_id:
            # Create new user
            user_id = str(uuid.uuid4())
            users_db[user_id] = {
                'id': user_id,
                'email': email,
                'name': email.split('@')[0],  # Use part of email as name
                'photos': []
            }
        
        # Set user in session
        session['user'] = user_id
        
        # Clear OTP
        del otp_db[email]
        
        # Redirect to profile or previous page
        redirect_to = request.args.get('redirect')
        if redirect_to:
            return redirect(url_for(redirect_to))
        return redirect(url_for('profile'))
    
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    otp = request.form.get('otp')
    
    # Validate inputs
    if not name or not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash('Invalid name or email address')
        return redirect(url_for('login'))
    
    # Check if OTP is provided
    if not otp:
        # Generate and send OTP
        new_otp = generate_otp()
        otp_db[email] = {
            'otp': new_otp,
            'expires': datetime.now() + timedelta(minutes=10)
        }
        send_otp_email(email, new_otp)
        flash(f'OTP sent to {email}')
        return render_template('login.html', name=name, email=email, show_otp=True, is_signup=True)
    
    # Verify OTP
    if email not in otp_db or otp_db[email]['otp'] != otp:
        flash('Invalid OTP')
        return redirect(url_for('login'))
    
    # Check if OTP is expired
    if datetime.now() > otp_db[email]['expires']:
        flash('OTP expired')
        return redirect(url_for('login'))
    
    # Check if user already exists
    for user in users_db.values():
        if user['email'] == email:
            flash('User with this email already exists')
            return redirect(url_for('login'))
    
    # Create new user
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        'id': user_id,
        'email': email,
        'name': name,
        'photos': []
    }
    
    # Set user in session
    session['user'] = user_id
    
    # Clear OTP
    del otp_db[email]
    
    # Redirect to profile
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']
    user = users_db.get(user_id)
    
    if not user:
        session.pop('user', None)
        return redirect(url_for('login'))
    
    # Get user's photos
    user_photos = []
    for photo_id in user['photos']:
        if photo_id in photos_db:
            user_photos.append(photos_db[photo_id])
    
    user['photos'] = user_photos
    
    return render_template('profile.html', user=user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/save_photo', methods=['POST'])
def save_photo():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    if 'processed_photo' not in session:
        return jsonify({'success': False, 'message': 'No photo to save'})
    
    user_id = session['user']
    user = users_db.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    # Get photo data from request
    photo_url = request.form.get('photo_url')
    background_color = request.form.get('background_color')
    
    if not photo_url:
        return jsonify({'success': False, 'message': 'No photo provided'})
    
    # Create new photo entry
    photo_id = str(uuid.uuid4())
    photos_db[photo_id] = {
        'id': photo_id,
        'url': photo_url,
        'background_color': background_color,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': user_id
    }
    
    # Add photo to user's photos
    user['photos'].append(photo_id)
    
    return jsonify({'success': True, 'message': 'Photo saved successfully'})

@app.route('/download_photo', methods=['POST'])
def download_photo():
    # Get photo data from request
    photo_url = request.form.get('photo_url')
    background_color = request.form.get('background_color')
    
    if not photo_url:
        return jsonify({'success': False, 'message': 'No photo provided'})
    
    # In a real application, you would generate the final image with the selected background color
    # For demo purposes, we'll just return success
    return jsonify({'success': True, 'download_url': photo_url})

@app.route('/apply_background', methods=['POST'])
def apply_background():
    if 'processed_photo' not in session:
        return jsonify({'success': False, 'message': 'No photo to edit'})
    
    # Get the processed photo path and background color
    photo_path = session['processed_photo']
    background_color = request.form.get('background_color', '#FFFFFF')
    
    try:
        # Convert hex color to RGB
        bg_color = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        bg_color = bg_color + (255,)  # Add alpha channel
        
        # Open the transparent image
        img = cv2.imread(photo_path, cv2.IMREAD_UNCHANGED)
        
        # Create a background of the specified color
        h, w = img.shape[:2]
        background = np.full((h, w, 4), bg_color, dtype=np.uint8)
        
        # Extract alpha channel from the image
        alpha = img[:, :, 3]
        
        # Convert alpha to 3 channel
        alpha_3channel = cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR)
        
        # Normalize alpha to range 0-1
        alpha_normalized = alpha / 255.0
        
        # Blend the image with the background using the alpha channel
        foreground = img[:, :, :3]
        for c in range(3):
            background[:, :, c] = background[:, :, c] * (1 - alpha_normalized) + foreground[:, :, c] * alpha_normalized
        
        # Save the result
        result_path = photo_path.replace('_transparent.png', f'_with_bg_{background_color[1:]}.png')
        cv2.imwrite(result_path, background)
        
        return jsonify({
            'success': True, 
            'photo_url': '/' + result_path
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error applying background: {str(e)}'})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

