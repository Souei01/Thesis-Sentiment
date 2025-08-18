# Thesis-Sentiment


## Thesis-Sentiment

This project consists of a Next.js client and a Python (Django) backend for sentiment analysis.

---

### Prerequisites

- [Node.js](https://nodejs.org/) (latest LTS recommended)
- [Python](https://www.python.org/) (3.8+ recommended)

---

## Setup Instructions

### 1. Client (Next.js)

1. Open a terminal and navigate to the `client` folder:
    ```powershell
    cd client
    ```
2. Install dependencies:
    ```powershell
    npm install
    ```
3. Start the development server:
    ```powershell
    npm run dev
    ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 2. Server (Python/Django)

1. (Recommended) Create and activate a virtual environment:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
2. Navigate to the `server` folder:
    ```powershell
    cd server
    ```
3. Install Python dependencies:
    ```powershell
    pip install -r requirements.txt
    ```
4. Run the Django server:
    ```powershell
    python manage.py runserver
    ```
5. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to access the backend.

---

## Notes

- Make sure your virtual environment is activated before installing Python packages or running the server.
- If you encounter issues with PowerShell script execution, set the execution policy:
    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    ```

---
