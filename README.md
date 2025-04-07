# Project Name: Passport Size Photo Maker AI

## Overview
This project is a Flask-based web application developed by Soham, designed to help users generate passport-sized photos with custom background colors using AI. Users can upload their image, which is then processed to remove the background. The app then allows users to select a new background color and download the final photo.

## Features
- AI-powered background removal using `rembg`
- User image upload and real-time preview
- Background color selection
- Downloadable passport-sized photo output
- Simple and responsive user interface

## File Structure
```
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html          # Homepage with image upload
│   ├── edit.html           # Image editing and background selection
│   ├── profile.html        # Placeholder (not actively used in main flow)
│   ├── login.html          # Placeholder (not actively used in main flow)
│   ├── contact.html        # Contact page
│   ├── about.html          # About the application
│   └── base.html           # Base template for shared layout
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/passport-photo-maker-ai.git
   cd passport-photo-maker-ai
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App
```bash
python app.py
```
The application will start on `http://127.0.0.1:5000/`

## Workflow
1. User visits the homepage (`index.html`) and uploads an image.
2. Image is processed using `rembg` to remove the background.
3. User is redirected to `edit.html`, where the image with the removed background is displayed.
4. User selects a background color.
5. A final image is generated with the selected background color.
6. User can download the passport-sized photo.

## Dependencies
- Flask
- OpenCV (`opencv-python`)
- Pillow
- rembg

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contact
For any inquiries or issues, please reach out via the contact page in the application.

