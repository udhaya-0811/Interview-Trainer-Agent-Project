# Interview Trainer Agent 🎯

A production-quality AI interview coach powered by **IBM Granite** (via IBM watsonx.ai)
and a RAG (Retrieval-Augmented Generation) pipeline over a curated knowledge base.

---

## Features

| Feature | Description |
|---|---|
| **Profile & Resume Parsing** | Upload PDF/DOCX or paste resume text; extracts skills, projects, and education |
| **Question Set Generation** | Grouped by Technical, Behavioral (STAR), HR/Situational, and Resume-based |
| **Model Answers** | Granite-generated answers with citations to the knowledge base |
| **Mock Interview Mode** | One-question-at-a-time with rubric scoring (clarity, correctness, depth, structure, communication) |
| **Evaluation Feedback** | Strengths, gaps, and an AI-rewritten improved answer per question |
| **Prep Plan Export** | Week-by-week plan downloadable as Markdown |
| **Session History** | SQLite-backed history with progress charts |
| **Grounded Answers** | Every answer shows which knowledge-base chunks were used |

---

## Architecture

```
User → Streamlit UI
  ↓
Profile & Resume Parsing  (resume_parser.py)
  ↓
RAG Pipeline:
  Knowledge Base (Markdown files) → Chunker → Sentence-Transformers Embeddings → FAISS/Vector Search
  ↓ top-k chunks + metadata
Prompt Construction → IBM Granite (watsonx.ai) → Structured JSON output
  ↓
Question Set / Evaluation / Prep Plan
  ↓
SQLite Session Store → Progress Charts
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- An IBM Cloud account (free Lite plan works)
- Access to IBM watsonx.ai

### 2. Get IBM watsonx.ai Credentials

1. Create a free IBM Cloud account at [https://cloud.ibm.com](https://cloud.ibm.com)
2. Navigate to **watsonx.ai**: [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
3. Click **Create project** → give it a name → note the **Project ID** (visible in the project settings URL)
4. Generate an **API key**:
   - Go to [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
   - Click **Create an IBM Cloud API key**
   - Copy and save the key (shown only once)
5. Note your **Service URL** based on your region:
   - US South: `https://us-south.ml.cloud.ibm.com`
   - EU DE: `https://eu-de.ml.cloud.ibm.com`
   - EU GB: `https://eu-gb.ml.cloud.ibm.com`
   - JP TOK: `https://jp-tok.ml.cloud.ibm.com`

### 3. Configure Environment

```bash
cd interview_trainer
cp .env.example .env
```

Edit `.env`:
```env
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_watsonx_project_id_here
```

> **Never commit the `.env` file.** It is in `.gitignore` by default.

### 4. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# Install packages
pip install -r requirements.txt
```

> **Note on sentence-transformers:** The first run downloads the `all-MiniLM-L6-v2`
> embedding model (~90 MB). This is cached locally for subsequent runs.

### 5. Run the App

```bash
cd interview_trainer          # must be in the interview_trainer/ directory
streamlit run app.py
```

The app opens at `http://localhost:8501`.

> **Alternative (from project root):**
> ```bash
> streamlit run interview_trainer/app.py
> ```

---

## Running Tests

```bash
cd interview_trainer          # project root containing tests/
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=interview_trainer --cov-report=term-missing
```

Tests use mocked Granite clients — **no real API calls** are made during testing.

---

## Project Structure

```
interview_trainer/
├── app.py                    # Streamlit entry point
├── config.py                 # All settings and constants
├── requirements.txt
├── .env.example              # Template for credentials
│
├── core/
│   ├── resume_parser.py      # PDF/DOCX/text resume extraction
│   ├── knowledge_base.py     # Chunking, embedding (MiniLM), retrieval
│   ├── granite_client.py     # IBM watsonx.ai / Granite wrapper
│   ├── question_generator.py # RAG-powered question set generation
│   ├── evaluator.py          # Rubric-based answer scoring
│   ├── planner.py            # Prep plan generation
│   └── session_store.py      # SQLite history
│
├── ui/
│   ├── main.py               # Streamlit app shell and navigation
│   ├── helpers.py            # Shared UI utilities
│   └── pages/
│       ├── setup.py          # Profile setup + resume upload
│       ├── questions.py      # Question bank display
│       ├── mock_interview.py # Mock interview mode
│       ├── history.py        # Progress and session history
│       └── prep_plan.py      # Prep plan generation + download
│
├── knowledge_base/
│   ├── java_developer.md     # 30 Java Developer Q&As
│   ├── ai_ml_engineer.md     # 30 AI/ML Engineer Q&As
│   ├── data_analyst.md       # 30 Data Analyst Q&As
│   ├── frontend_developer.md # 30 Frontend Developer Q&As
│   ├── devops_engineer.md    # 25 DevOps Engineer Q&As
│   ├── product_manager.md    # 15 Product Manager Q&As
│   ├── behavioral_star.md    # 12 Behavioral STAR examples
│   ├── hr_guidelines.md      # 15 HR/Situational Q&As
│   └── soft_skills.md        # 10 Soft Skills Q&As
│
└── tests/
    ├── test_resume_parser.py
    ├── test_knowledge_base.py
    ├── test_evaluator.py
    ├── test_session_store.py
    └── test_granite_client.py
```

---

## Configuration

All settings are in [`config.py`](config.py). Key parameters:

| Variable | Default | Description |
|---|---|---|
| `WATSONX_MODEL_ID` | `ibm/granite-3-8b-instruct` | Override with env var |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local sentence-transformers model |
| `RETRIEVAL_TOP_K` | `5` | Chunks retrieved per query |
| `LLM_MAX_NEW_TOKENS` | `1024` | Max tokens per generation |
| `LLM_TEMPERATURE` | `0.3` | Lower = more deterministic |
| `LLM_MAX_RETRIES` | `3` | API retry attempts |

---

## IBM Granite & watsonx.ai

This project exclusively uses **IBM Granite** models for all LLM calls. Granite models are:
- Developed by IBM, trained on curated enterprise data
- Commercially indemnified (safe for enterprise use)
- Available via the IBM watsonx.ai Lite (free) plan

The default model is `ibm/granite-3-8b-instruct`. Available models depend on your
watsonx.ai instance. Override with `WATSONX_MODEL_ID` environment variable.

---

## Adding New Roles

1. Create a Markdown file in `knowledge_base/`:
   ```
   knowledge_base/backend_engineer.md
   ```
2. Follow the format: `## Q{n} | difficulty: beginner/intermediate/advanced`
3. Add the role to `SUPPORTED_ROLES` in `config.py`:
   ```python
   "Backend Engineer": "backend_engineer",
   ```
4. Restart the app — the knowledge base rebuilds automatically.

---

## Screenshots

> _Run the app and take screenshots of each page to add here._

- Setup Profile page
- Question Bank with model answers and citations
- Mock Interview with real-time evaluation
- Rubric scores with strengths and gaps
- Progress chart over sessions
- Preparation plan with download

---

## Troubleshooting

| Error | Solution |
|---|---|
| `GraniteCredentialsError: Missing WATSONX_API_KEY` | Create `.env` from `.env.example` |
| `RuntimeError: sentence-transformers is not installed` | `pip install sentence-transformers` |
| `RuntimeError: pdfplumber is not installed` | `pip install pdfplumber` |
| `RuntimeError: python-docx is not installed` | `pip install python-docx` |
| Knowledge base builds slowly on first run | Embeddings computed once; cached in memory per session |
| `ibm-watsonx-ai` 401 error | Check API key is valid and not expired at cloud.ibm.com/iam/apikeys |

---

## License

MIT License. See LICENSE file for details.

---

*Built with IBM Granite on watsonx.ai · sentence-transformers · Streamlit · SQLite*
