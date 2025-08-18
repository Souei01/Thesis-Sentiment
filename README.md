# Thesis-Sentiment

Setup Instructions

Install Node.js and Python
Download and install the latest versions of Node.js and Python from their official websites.

Set up the client (Next.js app):
    Open a terminal and navigate to the client folder:
        #cd client
    Install dependencies:
        #npm install
    Start the development server:
        #npm run dev
Open the link shown in the terminal (usually http://localhost:3000) in your browser.

Set up the server (Python backend):
    activitate venv
        #.\venv\Scripts\activate
    Navigate to the server folder:
        #cd server
    Install Python dependencies
        #pip install -r requirements.txt

# How to run the Python server

## Activate your virtual environment (if not already active)
```
cd server
python -m venv venv
venv\Scripts\activate
```

## Run the server (example for Django)
```
python manage.py runserver
```

The server will start and show a local link (usually http://127.0.0.1:8000). Open this link in your browser to access the backend.
