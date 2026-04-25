# AI Citation Optimizer

AI Citation Optimizer is a specialized tool designed to help websites improve their visibility in AI search engines like ChatGPT, Perplexity, and Gemini. It detects pages ignored by AI engines, analyzes crawlability issues, and provides actionable optimization steps.

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **AI Agent**: Playwright (for rendered HTML analysis) + Gemini 1.5 Flash
- **Data Provider**: Peec AI API (for citation metrics and domain visibility)
- **Frontend**: React + Vite (Vanilla CSS Premium Design)

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the root directory (based on `.env.example`):

```env
PEEC_API_KEY=your_peec_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## 🐳 Running with Docker (Recommended)

Docker is the easiest way to run the app as it pre-configures all Playwright browser dependencies.

### Run everything with Docker Compose

```bash
# Build and start both services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop services
docker-compose down
```

### Build & Run Individual Containers (Optional)

**Backend:**

```bash
cd backend
docker build -t ai-citation-backend .
docker run -p 8000:8000 --env-file ../.env ai-citation-backend
```

**Frontend:**

```bash
cd frontend
docker build -t ai-citation-frontend .
docker run -p 5173:5173 ai-citation-frontend
```

---

## 🛠️ Running without Docker (Manual)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Start the Application

**Start Backend:**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Start Frontend:**

```bash
cd frontend
npm run dev
```

---

## API Endpoints

- `GET /api/gaps?domain=<domain>`: Returns a list of pages in the sitemap that are not currently cited by AI.
- `POST /api/audit`: Conducts a deep crawlability and AI-readiness audit of a specific URL.
- `GET /api/benchmark?domain=<domain>`: Provides visibility metrics and projected improvement scores.

## Example Usage

1. Enter your domain (e.g., `peec.ai`) on the Dashboard.
2. View the list of non-cited pages.
3. Click "Run Audit" on a page to see why it's ignored.
4. Apply the recommended fixes (e.g., reducing JS dependency, improving content clarity).
5. Track potential growth in the Benchmark section.
