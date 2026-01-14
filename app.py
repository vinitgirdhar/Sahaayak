from my_app import create_app, db

# Create the Flask app instance using the factory function
app = create_app()

# Initialize database on startup
with app.app_context():
    db.init_db()

# This is the entrypoint that Vercel will use
if __name__ == '__main__':
    app.run()
