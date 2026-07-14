# JobSense — Backend

AI-powered CV-to-job matcher. Upload a CV (PDF) and paste a job description;
JobSense returns a match score, matching skills, missing skills, and specific
improvement suggestions grounded in retrieved career-advice snippets (RAG).

---

## Architecture

```
React Frontend
      │
      ▼
FastAPI Backend
      │
      ├── PDF Extraction (pdfplumber)
      │
      ├── RAG Layer  ← Day 2
      │     ├── Embed job description (sentence-transformers)
      │     ├── Cosine similarity search over career-advice snippets
      │     └── Return top 3-5 relevant snippets
      │
      ├── Groq API (Llama 3.3 70B)
      │     └── CV + JD + retrieved snippets → structured JSON analysis
      │
      └── PostgreSQL  ← Day 4
            └── Save analysis results (no raw CV stored)
```

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | FastAPI                           |
| LLM        | Groq API (Llama 3.3 70B) — free   |
| PDF        | pdfplumber                        |
| Embeddings | sentence-transformers (local)     |
| Retrieval  | In-memory cosine similarity       |
| Database   | PostgreSQL + SQLAlchemy async     |
| Frontend   | React + TypeScript + Tailwind     |
| Validation | Pydantic v2                       |

## API Endpoints

```
POST /api/v1/analyze      # Upload CV + paste JD → returns analysis
GET  /api/v1/analyses     # List of past analyses
```

## Project Structure

```
jobsense_be/
├── app/
│   ├── main.py                      # FastAPI entrypoint, CORS, router
│   ├── core/
│   │   └── config.py                # env vars (GROQ_API_KEY, settings)
│   ├── routes/
│   │   └── analyze.py               # POST /api/v1/analyze endpoint
│   ├── services/
│   │   ├── pdf_service.py           # validates + extracts CV text      ✅ Day 1
│   │   ├── groq_service.py          # Groq/Llama call + JSON parsing    ✅ Day 1
│   │   ├── embedding_service.py     # embed text via local model        ← Day 2
│   │   └── retrieval_service.py     # cosine similarity search          ← Day 2
│   ├── schemas/
│   │   └── analysis.py              # Pydantic response schema          ✅ Day 1
│   ├── models/
│   │   └── analysis.py              # SQLAlchemy DB model               ← Day 4
│   └── data/
│       └── career_snippets.json     # 20-30 career-advice snippets      ← Day 2
├── alembic/                         # DB migrations                     ← Day 4
├── .env                             # secrets — never committed
├── requirements.txt
└── README.md
```

---

## Build Order

| Day   | Focus                                          | Status      |
|-------|------------------------------------------------|-------------|
| Day 1 | FastAPI skeleton, PDF extraction, Groq service | ✅ Complete  |
| Day 2 | RAG layer — snippets, embeddings, retrieval    | 🔄 Next      |
| Day 3 | Inject retrieved snippets into Groq prompt     | ⏳ Pending   |
| Day 4 | PostgreSQL model + save/retrieve analyses      | ⏳ Pending   |
| Day 5 | React frontend — upload form + results display | ⏳ Pending   |
| Day 6 | Polish — error states, loading, styling        | ⏳ Pending   |
| Day 7 | README + demo recording + push to GitHub       | ⏳ Pending   |

---

## Setup

### 1. Get your Groq API key (free, no credit card)
1. Go to **console.groq.com** and sign up
2. Go to **API Keys → Create API Key**
3. Copy the key — starts with `gsk_...`

### 2. Create your `.env` file
In the `jobsense_be/` root:
```
GROQ_API_KEY=gsk_...
```
Never commit this file — it's in `.gitignore`.

### 3. Install dependencies
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/health` → should return `{"status": "ok"}`
Visit `http://127.0.0.1:8000/docs` for auto-generated API docs.

### 5. Test via Postman
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/analyze`
- Body: `form-data`
  - `cv_file` → type **File**, select a PDF CV
  - `job_description` → type **Text**, paste a job description

**Expected response:**
```json
{
  "job_title": "Full Stack Engineer",
  "match_score": 85,
  "matching_skills": ["React", "Node.js", "JavaScript"],
  "missing_skills": ["AWS", "PostgreSQL"],
  "suggestions": [
    "Add specific metrics to your project descriptions...",
    "Highlight your REST API experience with concrete examples..."
  ]
}
```

### Troubleshooting
| Error | Cause | Fix |
|-------|-------|-----|
| `400` | Not a PDF or over 5MB | Use a valid text-based PDF under 5MB |
| `422` | PDF has no extractable text | Use a text-based PDF, not a scanned image |
| `502` | Groq response failed to parse | Check your API key; try again |
| `500` | Missing env variable | Confirm `.env` has `GROQ_API_KEY` set |

---

## Security Notes
- Raw CV text is never persisted — extracted in-memory, discarded after analysis
- Only analysis output is saved to the database (no PII from the CV)
- `expires_at` field on each analysis record — old records filtered out after 30 days
- `.env` excluded from git — secrets never committed