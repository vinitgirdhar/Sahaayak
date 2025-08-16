from my_app import create_app, db

# Create the Flask app instance using the factory function
app = create_app()

# This block ensures that the database is created if it doesn't exist
# when the application starts.
with app.app_context():
    db.init_db()

if __name__ == '__main__':
    # The 'debug=True' mode should be False in a production environment
    app.run(host='0.0.0.0', port=5000, debug=True)
