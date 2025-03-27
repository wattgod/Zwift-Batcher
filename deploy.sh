#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
SECRET_KEY=make-up-some-random-text
DATABASE_URL=sqlite:///workouts.db
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_BUCKET_NAME=gravel-god-workouts
AWS_REGION=us-west-2
UPLOAD_FOLDER=/path/to/uploads
EOL

# Create Procfile for Heroku
echo "web: gunicorn app:app" > Procfile

# Initialize database
python3 << EOL
from app import app, db
with app.app_context():
    db.create_all()
EOL

# Start the application
python3 app.py 