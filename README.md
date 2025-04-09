# Indian Passport Photo Generator

A web application that allows users to generate passport photos with custom background colors. The application removes the background from uploaded images and replaces it with a gradient background of the user's choice.

## Features

- Premium translucent dark theme UI
- Upload images via drag & drop or file selection
- Automatic background removal
- Selection of gradient background colors:
  - Red
  - Blue
  - Black
  - White
  - Cyan
  - Green
  - Purple
  - Pink
  - Maroon
- Download processed images

## File Structure

\`\`\`
passport_photo_generator/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── static/
│   ├── css/
│   │   └── style.css       # Application styles
│   ├── js/
│   │   └── script.js       # Client-side JavaScript
│   ├── uploads/            # Temporary storage for uploaded images
│   └── processed/          # Storage for processed images
└── templates/
    └── index.html          # Main application template
\`\`\`

## Installation

1. Clone the repository:
\`\`\`bash
git clone https://github.com/yourusername/passport_photo_generator.git
cd passport_photo_generator
\`\`\`

2. Create a virtual environment and activate it:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install the dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Run the application:
\`\`\`bash
python app.py
\`\`\`

5. Open your browser and navigate to `http://127.0.0.1:5000/`

## Requirements

- Python 3.8+
- Flask
- OpenCV
- NumPy
- Pillow
- rembg (for background removal)

## Usage

1. Upload an image by dragging and dropping it onto the upload area or by clicking the "Choose File" button.
2. Wait for the background removal process to complete.
3. Select a background color from the available options.
4. Click the "Download Photo" button to save the processed image.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
