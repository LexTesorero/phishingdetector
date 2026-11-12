# Phishing Detection Application

A full-stack application combining a **React** frontend, a **FastAPI** backend, and a **Streamlit** dashboard for model visualization or administrative monitoring.

## Project Structure

```text
phishing-app/
├── backend/
│   ├── .venv/
│   ├── main.py
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── ... (other backend modules)
└── frontend/
    ├── public/
    ├── src/
    ├── package.json
    └── ... (React configuration & components)
```

---

## Prerequisites

Ensure you have the following installed on your system:
* **Python 3.9+**
* **Node.js (v18+ recommended)** and **npm**

---

## 1. Backend Setup (FastAPI & Streamlit)

Open a terminal inside the root `phishing-app` directory and set up the Python environment:

```bash
mkdir -p backend
cd backend
python -m venv .venv
```

Activate the virtual environment:
* **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```
* **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate
  ```
* **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

Install the required Python dependencies (make sure your `requirements.txt` and four backend files are inside `backend/`):
```bash
pip install -r requirements.txt
```

---

## 2. Frontend Setup (React)

Open a terminal inside the root `phishing-app` directory. 

### If creating the React app from scratch (using Vite):
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

### If the `frontend` folder already exists:
```bash
cd frontend
npm install
```

### Connecting React to FastAPI
1. Create a `.env` file inside the `phishing-app/frontend/` directory to store your backend API URL:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
   *(Note: If using Create React App instead of Vite, name the variable `REACT_APP_API_URL=http://localhost:8000`).*

2. Ensure **CORS** is enabled in your FastAPI `main.py` so the React dev server (usually running on port `5173` for Vite or `3000` for CRA) can communicate with port `8000`:
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI()

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173", "http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## 3. Running the Application (3 Terminals)

To run the full stack locally, open **three separate terminal windows** from the `phishing-app` root directory:

### Terminal 1: React Frontend
```bash
cd phishing-app/frontend
npm run dev
```
*Runs at `http://localhost:5173` (or `http://localhost:3000` depending on your React setup).*

### Terminal 2: FastAPI Backend
```bash
cd phishing-app/backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn main:app --reload --port 8000
```
*API runs at `http://localhost:8000` | Interactive docs at `http://localhost:8000/docs`.*

### Terminal 3: Streamlit Dashboard
```bash
cd phishing-app/backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
streamlit run streamlit_app.py
```
*Dashboard runs at `http://localhost:8501`.*