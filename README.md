# Manak Mitra — AI-Powered Indian Standards Recommender

> Hackathon prototype for SIH 2026: An AI-powered tool that recommends applicable Indian Standards (IS) for procurement tender specifications.

## 🎯 What it Does

1. **Upload** a tender document (PDF/DOCX/TXT) or paste tender text
2. **Extract** technical/performance/safety requirements using AI (LLM)
3. **Recommend** ranked Indian Standards (IS) via hybrid search (FAISS + BM25)
4. **Review** — Accept ✓, Reject ✗, or Flag 🚩 each recommendation
5. **Export** a downloadable PDF/DOCX report of approved standards

## 🏗️ Architecture

```
Frontend (Next.js :3000)  →  Backend (FastAPI :8000)
                                ├── LLM (OpenAI-compatible)
                                ├── FAISS + BM25 hybrid search
                                └── SQLite database
```

## 📦 Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- (Optional) An OpenAI-compatible API key for real LLM-based extraction

## 🚀 Quick Start

### 1. Clone and Setup Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend will:
- Create SQLite database and tables
- Seed 40 Indian Standards entries
- Build FAISS + BM25 search indexes
- Start at http://localhost:8000

> ⚠️ First run downloads the sentence-transformer model (~90MB). This takes a minute.

### 2. Setup Frontend

```bash
cd frontend

# Install Node dependencies (already done if you just scaffolded)
npm install

# Start the dev server
npm run dev
```

Frontend runs at http://localhost:3000

### 3. (Optional) Configure LLM

Copy `.env.example` to `.env` and set your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

**Without an API key**, the app runs in demo mode using keyword-based extraction.

## 📂 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app with CORS + lifespan
│   ├── config.py             # Environment config
│   ├── database.py           # SQLAlchemy setup
│   ├── models.py             # ORM models (5 tables)
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── seed_db.py            # Database seeder
│   ├── routers/
│   │   ├── extract.py        # POST /api/extract
│   │   ├── recommend.py      # POST /api/recommend
│   │   ├── review.py         # PUT /api/review/{id}
│   │   ├── standards.py      # GET /api/standards
│   │   └── export.py         # POST /api/export
│   ├── services/
│   │   ├── llm_service.py    # LLM wrapper + mock fallback
│   │   ├── search_service.py # FAISS + BM25 hybrid search
│   │   ├── document_parser.py # PDF/DOCX text extraction
│   │   ├── export_service.py # PDF/DOCX report generation
│   │   └── stubs.py          # Future work stubs
│   └── seed/
│       ├── standards_data.json    # 40 Indian Standards
│       └── sample_tenders/        # 3 sample tender documents
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx           # Dashboard
│       │   ├── analysis/new/      # Upload page
│       │   ├── analysis/[id]/     # Results/review page
│       │   └── standards/         # Standards library
│       ├── components/            # Reusable UI components
│       └── lib/api.ts             # API client
└── .env.example
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/tenders` | List all tenders |
| GET | `/api/sample-tenders` | Get sample tender texts |
| POST | `/api/extract` | Extract requirements from tender |
| POST | `/api/recommend` | Get IS recommendations |
| GET | `/api/tenders/{id}/review` | Get tender review status |
| PUT | `/api/review/{id}` | Accept/reject/flag recommendation |
| GET | `/api/standards` | List/search standards |
| GET | `/api/standards/sectors` | List sectors |
| POST | `/api/export` | Export PDF/DOCX report |

## 🔮 Future Work

These features are stubbed in `services/stubs.py`:

- **Neo4j Knowledge Graph** — Standard relationships, lineage, cross-references
- **Sarvam AI Translation** — Multilingual support (Hindi, Tamil, etc.)
- **Live BIS API** — Real-time standard catalog lookup
- **GeM/CPPP Integration** — Marketplace and portal integration
- **Amendment Tracking** — Lifecycle and revision tracking

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15, Tailwind CSS, TypeScript |
| Backend | Python FastAPI, SQLAlchemy |
| AI/NLP | OpenAI-compatible LLM (GPT-4o-mini) |
| Search | FAISS (semantic) + BM25 (keyword) hybrid |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Database | SQLite |
| Export | ReportLab (PDF), python-docx (DOCX) |

## 📝 Demo

The app comes with:
- **40 Indian Standards** across construction, electrical, IT, food safety, plumbing, fire safety sectors
- **3 sample tenders**: construction, IT equipment, food supply
- Click "Load Sample Tender" on the upload page to try without a real document

---

*Built for Smart India Hackathon 2026*
