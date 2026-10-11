# SkillMap AI - Standalone Backend API

A high-performance FastAPI backend providing technology skill intelligence, real-time demand insights, verified salary benchmarks, and live job opportunities using Google Gemini and RapidAPI JSearch.

---

## 1. Quickstart & Local Setup (Windows / PowerShell)

### Prerequisites
- Python 3.12 (or 3.11+)
- Git

### Step 1: Navigate to the Backend Directory
```powershell
cd backend
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your credentials:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key
RAPIDAPI_KEY=your_actual_rapidapi_key
COMPOSIO_API_KEY=your_actual_composio_key
```

### Step 5: Start the FastAPI Server
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 2. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and root metadata |
| `GET` | `/api/health` | Lightweight service health check (no external API calls) |
| `POST` | `/api/query` | Submit skill demand & job inquiry |
| `GET` | `/docs` | Interactive Swagger UI / OpenAPI documentation |
| `GET` | `/redoc` | Interactive ReDoc documentation |

### Sample `POST /api/query` Request
```json
{
  "query": "What is the demand for Generative AI in the industry, and what jobs are open in India?",
  "location": "Bengaluru",
  "country": "in",
  "experience_level": "entry",
  "remote_only": false
}
```

---

## 3. Running the Automated Test Suite

All tests use mocks for external network calls and do not consume API credits or expose secrets.

```powershell
pytest -v
```

---

## 4. Render Deployment Configuration

When deploying the backend as a Web Service on [Render](https://render.com):

- **Environment:** `Python 3`
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/api/health`
- **Environment Variables to Configure in Render Dashboard:**
  - `GEMINI_API_KEY`
  - `RAPIDAPI_KEY`
  - `COMPOSIO_API_KEY`
  - `FRONTEND_ORIGINS` (Set to your production frontend URL, e.g., `https://your-frontend.vercel.app`)
  - `DEFAULT_COUNTRY` (`in`)
