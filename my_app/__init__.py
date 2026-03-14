import os
import shutil
from pathlib import Path

from flask import Flask

from config import Config


def _resolve_runtime_config(overrides=None):
    runtime_config = dict(overrides or {})

    if not os.getenv('VERCEL'):
        return runtime_config

    package_dir = Path(__file__).resolve().parent
    project_root = package_dir.parent
    runtime_root = Path('/tmp') / 'sahaayak_runtime'
    runtime_root.mkdir(parents=True, exist_ok=True)

    source_database = runtime_config.get('DATABASE', Config.DATABASE)
    source_database_path = Path(source_database)
    if not source_database_path.is_absolute():
        source_database_path = project_root / source_database_path

    runtime_database_path = runtime_root / 'vendor_clubs.db'
    if source_database_path.exists() and not runtime_database_path.exists():
        shutil.copy2(source_database_path, runtime_database_path)

    runtime_upload_dir = runtime_root / 'uploads'
    runtime_upload_dir.mkdir(parents=True, exist_ok=True)

    runtime_config.update({
        'DATABASE': str(runtime_database_path),
        'UPLOAD_FOLDER': str(runtime_upload_dir),
    })
    return runtime_config

def create_app(config_class=Config, config_overrides=None, static_folder=None):
    """Creates and configures the Flask application."""
    flask_kwargs = {'instance_relative_config': True}
    if static_folder is not None:
        flask_kwargs['static_folder'] = static_folder

    # Note the instance_relative_config=True.
    # This means the app can load config from an 'instance' folder outside the package.
    app = Flask(__name__, **flask_kwargs)
    
    # Load configuration from the config object
    app.config.from_object(config_class)
    app.config.update(_resolve_runtime_config(config_overrides))

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure upload directory exists
    # Note: We use app.config['UPLOAD_FOLDER'] which is now an absolute path
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Make API key available to all templates
    @app.context_processor
    def inject_api_key():
        return dict(GEMINI_API_KEY=app.config['GEMINI_API_KEY'])

    # Import and register the Blueprint from routes.py
    from . import routes
    app.register_blueprint(routes.bp)

    # A simple command to initialize the database from the command line
    # You can run 'flask init-db' in your terminal
    from . import db
    @app.cli.command('init-db')
    def init_db_command():
        """Clear the existing data and create new tables."""
        db.init_db()
        print('Initialized the database.')

    return app
