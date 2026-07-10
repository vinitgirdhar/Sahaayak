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
    # Prefer setting GEMINI_API_KEY via environment variable for security.
    # Fallback default updated per user request (consider moving this to .env or CI secrets).
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBsa_rDeTYEsioStJUsvH2hjkFFzwgPU00')
    
    # 9router gateway integration
    NINEROUTER_API_KEY = os.getenv('NINEROUTER_API_KEY', 'your-9router-key-here')
    NINEROUTER_API_BASE = os.getenv('NINEROUTER_API_BASE', 'https://api.9router.com/v1')
    NINEROUTER_MODEL_DEFAULT = os.getenv('NINEROUTER_MODEL_DEFAULT', 'gpt-4o-mini')
    NINEROUTER_MODEL_CHATBOT = os.getenv('NINEROUTER_MODEL_CHATBOT', 'gpt-4o-mini')
    NINEROUTER_MODEL_HINDI = os.getenv('NINEROUTER_MODEL_HINDI', 'gpt-4o-mini')
    NINEROUTER_MODEL_MARATHI = os.getenv('NINEROUTER_MODEL_MARATHI', 'gpt-4o-mini')
    NINEROUTER_MODEL_ENGLISH = os.getenv('NINEROUTER_MODEL_ENGLISH', 'gpt-4o-mini')

    # Fallback model lists
    NINEROUTER_MODELS_VOICE = [m.strip() for m in os.getenv('NINEROUTER_MODELS_VOICE', 'groq/whisper-large-v3,whisper-large-v3,openai/whisper-1').split(',') if m.strip()]
    NINEROUTER_MODELS_CHATBOT = [m.strip() for m in os.getenv('NINEROUTER_MODELS_CHATBOT', 'gpt-4o-mini').split(',') if m.strip()]
    NINEROUTER_MODELS_HINDI = [m.strip() for m in os.getenv('NINEROUTER_MODELS_HINDI', 'gpt-4o-mini').split(',') if m.strip()]
    NINEROUTER_MODELS_MARATHI = [m.strip() for m in os.getenv('NINEROUTER_MODELS_MARATHI', 'gpt-4o-mini').split(',') if m.strip()]
    NINEROUTER_MODELS_ENGLISH = [m.strip() for m in os.getenv('NINEROUTER_MODELS_ENGLISH', 'gpt-4o-mini').split(',') if m.strip()]

    # Database configuration
    DATABASE = 'vendor_clubs.db'

    # File upload configuration
    UPLOAD_FOLDER = 'my_app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

