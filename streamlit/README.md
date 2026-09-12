# Split Karo Streamlit UI

This is a standalone Streamlit client for the existing FastAPI backend. It does not modify or import the backend application.

## Run

From this directory:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

The app defaults to `http://127.0.0.1:8000/api/v1`. Start the existing backend separately, then change the backend URL in the sidebar if needed.

The client keeps the backend's session cookie in a server-side `requests.Session`; it does not use bearer tokens or expose secrets in the UI.