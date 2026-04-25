# AI Citation Optimizer

AI Citation Optimizer is a specialized tool designed to help websites improve their visibility in AI search engines like ChatGPT, Perplexity, and Gemini. It detects pages ignored by AI engines, analyzes crawlability issues, compares your brand against competitors across key channels, and provides actionable optimization steps with automated content drafting.

## Key Features

- **Competitor Advantage Breakdown:** Visualizes visibility gaps between your brand and top competitors across YouTube, Reddit, Editorial Lists, and Wikipedia.
- **Detailed Optimization Roadmap:** A prioritized action plan generated from your domain's AI citation gaps.
- **Automated Content Drafting:** Uses Gemini to instantly draft tailored YouTube collaboration pitches, Reddit comments, and PR emails.
- **Actionable Fix Instructions:** Provides specific problem analysis, step-by-step fixes, and copy-paste JSON-LD schema snippets for missing pages based on URL structures.
- **Deep Crawlability Audit:** Uses Headless Chromium (Playwright) to render JavaScript-heavy pages, calculating precise DOM depth, load times, and measuring JS-rendered text bloat to identify crawling bottlenecks.

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **AI Agent**: Playwright (for rendered HTML analysis) + Gemini 2.5 Flash
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

- `GET /api/gaps?domain=<domain>`: Returns a list of non-cited pages, overall performance metrics, and competitor visibility data.
- `GET /api/benchmark?domain=<domain>`: Provides the detailed optimization roadmap, competitor breakdown, and gap sources.
- `POST /api/audit`: Conducts a deep crawlability and AI-readiness audit of a specific URL.
- `POST /api/generate-fix`: Generates an actionable fix checklist and JSON-LD schema for a missing page.
- `POST /api/generate-content`: Drafts targeted outreach content (emails, comments, scripts) for specific optimization roadmap items.

## Example Usage

1. Enter your domain (e.g., `nothing.tech`) on the Dashboard.
2. Review the **Growth Opportunity** and **Competitor Advantage Breakdown** to see where you stand.
3. Check the **Optimization Roadmap** for high-priority actions and click "Draft Content" to instantly generate outreach emails or comments.
4. Drill down into specific **Gap Sources** (YouTube, Reddit, Editorial) to identify missed citation opportunities.
5. In the **Pages Missing** section, click "How to Fix" to get specific, step-by-step instructions and JSON-LD markup to make the page AI-ready.
