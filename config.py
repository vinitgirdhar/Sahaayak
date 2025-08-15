import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, environment variables should be set manually
    pass

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'a-very-secret-key-that-you-should-change')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDyYEw7SLwswMtutVhtUy0zI2bvaf_SIdU')
    
    # Database configuration
    DATABASE = 'vendor_clubs.db'

    # File upload configuration
    UPLOAD_FOLDER = 'my_app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

