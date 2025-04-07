# Project Name: Image Background Removal Web App

## Overview
This project is a Flask-based web application designed to remove backgrounds from images using AI-powered tools. The app allows users to upload images, process them to remove backgrounds using the `rembg` library, and download the edited result. The frontend consists of various HTML templates for user interaction.

## Features
- User registration and login system
- Image upload and processing
- Background removal using `rembg`
- Profile and edit pages for user details
- Responsive frontend built with HTML/CSS

## File Structure
```
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html          # Homepage
│   ├── login.html          # Login page
│   ├── profile.html        # User profile page
│   ├── edit.html           # Edit user details page
│   ├── contact.html        # Contact page
│   ├── about.html          # About page
│   └── base.html           # Base template for reuse
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/image-bg-remover.git
   cd image-bg-remover
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

## Dependencies
- Flask
- OpenCV (opencv-python)
- Pillow
- rembg

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contact
For any inquiries or issues, please reach out via the contact page in the application.

