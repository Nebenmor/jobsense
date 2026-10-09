# JobSense

AI-powered CV-to-job matcher built on a Retrieval-Augmented Generation (RAG) architecture. JobSense analyzes a candidate's CV against a job description and returns a structured match assessment — score, skill alignment, gaps, and improvement suggestions grounded in retrieved reference material.

---

![JobSense](./screenshot.png)

---

## Live

**Application:** https://jobsense-nine.vercel.app
**API Documentation:** https://jobsense-lvrs.onrender.com/docs

---

## How It Works

The core pipeline follows the RAG pattern: retrieve relevant context, augment the prompt with that context, then generate a grounded response.

```
CV (PDF) + Job Description
          │
          ▼
    PDF Text Extraction
    (pdfplumber — in-memory only, never persisted)
          │
          ▼
    RAG Retrieval
    (job description scored against 25 career-advice
     snippets using keyword similarity)
          │
          ▼
    Prompt Augmentation
    (CV text + JD + top 4 retrieved snippets)
          │
          ▼
    LLM Generation
    (Groq — Llama 3.3 70B — structured JSON output)
          │
          ▼
    Response Validation
    (Pydantic v2 — schema enforcement, score bounds)
          │
          ▼
    Persistence
    (PostgreSQL — analysis output only, not raw CV)
          │
          ▼
    Structured Response
    (match score, matching skills, gaps, suggestions)
```

### RAG Implementation

The retrieval step uses a static knowledge base of 25 career-advice snippets spanning categories including backend engineering, frontend development, cloud platforms, leadership, data engineering, DevOps, testing practices, and ATS optimisation.

At query time, the incoming job description is scored against all snippets using keyword-category matching. The top 4 most relevant snippets are injected into the LLM prompt before generation. This grounds the model's suggestions in specific retrieved reference material rather than relying on general training knowledge.

The result: a backend engineering job description retrieves advice on tool specificity, system design metrics, and testing practices — not advice written for mobile roles or cover letters.

---

## Architecture

```
┌─────────────────────┐         ┌──────────────────────────────────────────┐
│   React Frontend    │────────▶│              FastAPI Backend               │
│     (Vercel)        │         │               (Render)                     │
│                     │◀────────│                                            │
└─────────────────────┘         │  ┌──────────────┐  ┌───────────────────┐ │
                                 │  │ PDF Extraction│  │  RAG Retrieval    │ │
                                 │  │ (pdfplumber)  │  │  keyword scoring  │ │
                                 │  └──────────────┘  │  over 25 snippets │ │
                                 │                     └─────────┬─────────┘ │
                                 │                               │            │
                                 │                     ┌─────────▼─────────┐ │
                                 │                     │     Groq API       │ │
                                 │                     │  Llama 3.3 70B    │ │
                                 │                     └───────────────────┘ │
                                 └───────────────────────────────┬────────────┘
                                                                 │
                                                    ┌────────────▼───────────┐
                                                    │       PostgreSQL        │
                                                    │   (Neon serverless)    │
                                                    └────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Detail |
|-------|-----------|--------|
| Frontend | React 18 + TypeScript + Vite | Two-panel layout, animated SVG score ring |
| Styling | Plain CSS | No component library — custom design system |
| Backend | FastAPI (Python 3.11) | Fully async, Pydantic v2 request/response validation |
| LLM | Groq API — Llama 3.3 70B | Structured JSON output with retry and parse guards |
| PDF Parsing | pdfplumber | In-memory extraction, file discarded post-analysis |
| RAG | Keyword-based retrieval | 25 categorised career-advice snippets |
| Database | PostgreSQL (Neon) + SQLAlchemy (async) | asyncpg driver, serverless Postgres |
| Migrations | Alembic | Auto-applied on deploy via build command |
| Frontend Hosting | Vercel | Auto-deploy on push to main |
| Backend Hosting | Render | Free tier web service |

---

## Project Structure

```
jobsense/
├── backend/
│   ├── alembic/
│   │   ├── env.py                      # Alembic async migration runner
│   │   ├── script.py.mako              # Migration file template
│   │   └── versions/
│   │       └── xxxx_create_analyses_table.py
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic settings — loads from .env
│   │   │   └── database.py             # Async SQLAlchemy engine, session factory
│   │   ├── data/
│   │   │   └── career_snippets.json    # RAG knowledge base — 25 categorised snippets
│   │   ├── models/
│   │   │   └── analysis.py             # SQLAlchemy ORM model — analyses table
│   │   ├── routes/
│   │   │   └── analyze.py              # POST /api/v1/analyze
│   │   │                               # GET  /api/v1/analyses
│   │   │                               # GET  /api/v1/analyses/{id}
│   │   ├── schemas/
│   │   │   └── analysis.py             # Pydantic schemas — AnalysisResponse,
│   │   │                               # AnalysisSaved, AnalysisSummary
│   │   ├── services/
│   │   │   ├── pdf_service.py          # File type/size validation, text extraction
│   │   │   ├── groq_service.py         # Prompt construction, API call, JSON parsing
│   │   │   └── retrieval_service.py    # Keyword scoring, top-k snippet retrieval
│   │   └── main.py                     # FastAPI app, CORS middleware, router mounting
│   ├── alembic.ini
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── api/
        │   └── client.ts               # Axios instance, reads VITE_API_URL
        ├── components/
        │   ├── UploadForm.tsx           # PDF upload, job description input, submit
        │   ├── ResultsPanel.tsx         # Score, matching skills, gaps, suggestions
        │   ├── ScoreRing.tsx            # Animated SVG arc — score visualisation
        │   └── PastAnalyses.tsx         # Fetches and renders past analysis records
        ├── types/
        │   └── analysis.ts             # TypeScript interfaces — AnalysisResult,
        │                               # AnalysisSummary
        └── App.tsx                     # Root component, layout, state management
```

---

## API Reference

### `POST /api/v1/analyze`

Accepts a CV file and job description. Runs the full RAG pipeline and returns a structured analysis.

**Request:** `multipart/form-data`

| Field | Type | Constraints |
|-------|------|-------------|
| `cv_file` | File | PDF only, max 5MB, must contain extractable text |
| `job_description` | string | Plain text, required |

**Response:** `200 OK`

```json
{
  "id": "3f7a1c2e-...",
  "job_title": "Senior Backend Engineer",
  "match_score": 78,
  "matching_skills": ["FastAPI", "PostgreSQL", "REST API design"],
  "missing_skills": ["Kubernetes", "AWS"],
  "suggestions": [
    "Quantify the scale of the APIs you have built — include request volume or latency metrics.",
    "Add specific AWS services by name rather than listing 'cloud experience'."
  ],
  "created_at": "2026-07-17T10:30:00Z",
  "expires_at": "2026-08-16T10:30:00Z"
}
```

**Error responses:**

| Status | Cause |
|--------|-------|
| `400` | File is not a PDF or exceeds 5MB |
| `422` | PDF contains no extractable text (scanned/image-based) |
| `502` | LLM response could not be parsed after two attempts |

---

### `GET /api/v1/analyses`

Returns all non-expired analyses ordered by creation date descending.

**Response:** `200 OK` — array of `AnalysisSummary` objects (id, job_title, match_score, created_at)

---

### `GET /api/v1/analyses/{id}`

Returns a single analysis by ID with full detail.

**Response:** `200 OK` — full `AnalysisSaved` object

| Status | Cause |
|--------|-------|
| `404` | Analysis not found or past its expiry date |

---

## Data Model

```sql
CREATE TABLE analyses (
    id           VARCHAR PRIMARY KEY,     -- UUID
    job_title    VARCHAR,
    match_score  INTEGER,                 -- 0-100, enforced at schema level
    matching_skills  JSON,               -- string array
    missing_skills   JSON,               -- string array
    suggestions      JSON,               -- string array
    created_at   TIMESTAMPTZ,
    expires_at   TIMESTAMPTZ             -- 30 days from creation
);
```

Expired records are filtered at query time (`WHERE expires_at > now()`). Raw CV text and extracted PDF content are never written to the database — only the structured analysis output is persisted.

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Groq API key — free at [console.groq.com](https://console.groq.com)

### Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env` in `backend/`:

```env
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/jobsense
```

```bash
# Create the database
createdb jobsense

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

npm install
```

Create `.env.development` in `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

```bash
npm run dev
```

- App: `http://localhost:5173`

---

## Deployment

### Backend (Render)

Set the following environment variables in the Render dashboard:

| Variable | Value |
|----------|-------|
| `GROQ_API_KEY` | Your Groq API key |
| DATABASE_URL   | Neon connection string (direct, non-pooled) |

**Build command:**
```
pip install -r requirements.txt && alembic upgrade head
```

**Start command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The build command runs Alembic migrations on every deploy. Alembic tracks applied migrations and skips those already run — safe to execute repeatedly.

### Frontend (Vercel)

Set the following environment variable in the Vercel dashboard:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Render backend URL |

Set root directory to `frontend`. Vercel auto-detects Vite and configures the build.

---

## Security

- CV files are processed in-memory and discarded immediately after text extraction — never written to disk or database
- Only structured analysis output (no PII) is persisted
- Analysis records are soft-expired after 30 days and excluded from all queries
- Secrets are managed via environment variables — never committed to source control
- PDF validation enforces file type and size limits before any processing occurs

---

## Design Decisions

**Groq over OpenAI or Anthropic**
Groq's free tier operates without region restrictions or upfront billing — important for development accessibility. Llama 3.3 70B produces reliable structured JSON output for this task with `temperature=0.3`.

**Keyword retrieval over vector embeddings**
The initial implementation used `sentence-transformers` with cosine similarity. The model (~400MB) exceeded Render's 512MB free-tier RAM ceiling. For a 25-snippet static knowledge base, keyword-category scoring produces equivalent retrieval quality at a fraction of the memory cost. The RAG pattern — retrieve, augment, generate — is architecturally identical regardless of the scoring method.

**`asyncpg` + SQLAlchemy async**
FastAPI is an async framework. Using a synchronous database driver would block the event loop under concurrent requests. The async stack (asyncpg + SQLAlchemy async sessions) keeps the entire request lifecycle non-blocking.

**Alembic over `create_all`**
`Base.metadata.create_all` is convenient but provides no migration history, no rollback capability, and no safe path for schema changes in production. Alembic runs as part of the build command — the database schema is always in the state the codebase expects.

**Neon over Render Postgres**
Render's free PostgreSQL instances expire after 30 days. Neon's free tier does not expire; compute suspends when idle and wakes on the next query. The app handles this with `pool_pre_ping` and `pool_recycle`.

---

## Contributing

Pull requests are very welcome. For significant changes, open an issue first to discuss the proposed change.

---

## License

MIT

---

## Author

**Anthony Nebenmor**
[GitHub](https://github.com/Nebenmor) · [LinkedIn](https://linkedin.com/in/anthony-nebenmor)