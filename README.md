# LaunchWise

**A rule-based website planner for small businesses: answer five quick questions, get a ready-to-use website plan.**

![LaunchWise home page](docs/screenshots/home.png)

## The problem
A small business owner knows they need a website, but not *what kind*: which pages, which features, what to
write, what matters for Google, or what to ask a developer. Agencies answer these questions in a paid discovery
call; most owners just guess.

## The solution
A five-step wizard (business type, goal, audience, features, budget and timeline) turns the answers into a
clear website brief in about three minutes. The plan gets its own shareable link and can be copied or
downloaded as Markdown or plain text.

| Wizard | Result: sitemap | On a phone |
|---|---|---|
| ![Planner wizard](docs/screenshots/planner.png) | ![Plan with sitemap](docs/screenshots/plan-sitemap.png) | ![Plan on mobile](docs/screenshots/plan-mobile.png) |

## Features
- **Site type**: landing page, business site, booking site, online store or portfolio, with the reason it fits.
- **Sitemap**: every page with its sections, split into *launch now* and *later*; the budget decides the scope.
- **Features with priorities**: must-have and nice-to-have, including useful ones the user didn't pick.
- **Content ideas** for each launch page, tailored to the business type.
- **SEO starter checklist** (10–14 items, grouped) with a progress ring saved in the browser.
- **Complexity estimate**: a 1–10 score, a label and estimated weeks, with the scoring explained.
- **Export**: copy the brief, download `.md` / `.txt`, copy a share link.
- **Recent plans** kept only in the browser (no accounts).
- **Similar live sites** from the [FreeSerp](https://freeserp.ai) API (optional, `FREESERP_ENABLED`), cached and with a safe fallback.
- Accessible (WCAG 2.1 AA checked with axe), responsive from 390 px, keyboard-friendly.

## How the rule engine works
The plan is produced by a transparent, deterministic rule engine (`backend/app/rules.py`), **not an LLM**:
the same answers always give the same plan, and every item carries a short "why".

1. **Site type**: the business type gives a base (salon → booking site); the goal can change it
   (sell online → online store); leads on a starter budget → a single landing page.
2. **Features**: the user's picks plus recommendations triggered by the goal, languages, audience and business type.
   If several rules recommend the same feature, *must* beats *nice* and the strongest rule's reason is kept.
3. **Sitemap**: business pages first, then pages for picked/must features, then engine extras (FAQ).
   The budget sets how many go live at launch (4 / 6 / all). Required pages (Privacy & imprint, and Shipping & returns
   for stores) are always launched and never counted.
4. **Complexity**: site-type base + feature weights (+1 for 7+ launch pages), capped at 10.
5. **Content ideas, SEO checklist, next steps and summary** are derived from the above; every number in the text is
   computed from the generated sitemap.

Each saved plan stores the `engine_version` that produced it, so shared links keep showing the original result.

## Tech stack
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS 4, React Router, lucide-react
- **Backend:** Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2, PyMySQL, httpx, managed with uv
- **Database:** MariaDB 11.8 (Docker for local development)
- **Testing:** pytest, Playwright, axe-core
- **Production:** nginx (reverse proxy, rate limiting), systemd

## Architecture
```mermaid
flowchart LR
    U[Browser] --> FE[React + Vite SPA]
    FE -- "/api (JSON)" --> API[FastAPI]
    API --> RE[Rule engine<br/>rules.py]
    API --> DB[(MariaDB<br/>saved plans)]
    API -. "cached, optional" .-> FS[FreeSerp API<br/>example sites]
```

API: `GET /api/health`, `GET /api/options`, `POST /api/plans`, `GET /api/plans/{id}`,
`GET /api/plans/{id}/export?format=md|txt`, `GET /api/examples?business_type=…` (OpenAPI docs at `/api/docs`).

## Run locally
Requirements: Docker, Node.js 22+, Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).
```bash
git clone https://github.com/<your-user>/launchwise.git && cd launchwise

# 1. settings: one .env in the repo root for Docker, backend and frontend
cp .env.example .env
#    set MARIADB_ROOT_PASSWORD and MARIADB_PASSWORD, and use the same password in DATABASE_URL

# 2. database (the plans table is created on first start from backend/sql/)
docker compose up -d
docker compose ps                     # wait until "healthy"

# 3. backend (terminal 1)
cd backend
uv sync
uv run python -m scripts.seed_demo    # optional: three demo plans
uv run uvicorn app.main:app --reload --port 8000

# 4. frontend (terminal 2)
cd frontend
npm ci
npm run dev                           # http://localhost:5173, proxies /api to :8000
```
Open http://localhost:5173 (demo plan: http://localhost:5173/plan/l34kndqa5h).
Stop the database with `docker compose down` (`down -v` also deletes its data).

## Environment variables
All settings live in one `.env` in the repo root (see [`.env.example`](.env.example)).

| Variable | Used by | Required | Example / default | Purpose |
|---|---|---|---|---|
| `MARIADB_ROOT_PASSWORD` | docker compose | yes | `change-me-root` | MariaDB root password |
| `MARIADB_DATABASE` | docker compose | no | `launchwise` | Database name |
| `MARIADB_USER` | docker compose | no | `launchwise` | Application DB user |
| `MARIADB_PASSWORD` | docker compose | yes | `change-me` | Application DB password |
| `MARIADB_PORT` | docker compose | no | `3307` | Host port for MariaDB |
| `DATABASE_URL` | backend | yes | `mysql+pymysql://launchwise:change-me@127.0.0.1:3307/launchwise?charset=utf8mb4` | SQLAlchemy connection string |
| `FREESERP_ENABLED` | backend | no | `true` | `false` skips example sites (no outside requests) |
| `FREESERP_URL` | backend | no | `https://freeserp.ai/api.php` | FreeSerp endpoint (no API key needed) |
| `VITE_SITE_URL` | frontend | no | `http://localhost:5173` | Public URL for canonical / Open Graph tags |
| `VITE_API_PROXY_TARGET` | frontend (dev) | no | `http://127.0.0.1:8000` | Where the Vite dev server sends `/api` |

## Testing
```bash
# backend unit tests (1,000+ cases: rules, schemas, export, FreeSerp client, API errors)
cd backend && uv run pytest -q

# end-to-end and accessibility checks (Playwright), against a running site
uv run --with playwright playwright install chromium
uv run --with playwright python qa/wizard_e2e.py http://localhost:5173    # wizard: validation, keyboard, reload, errors
uv run --with playwright python qa/plan_e2e.py http://localhost:5173      # result page: tabs, export, share, page counts
uv run --with playwright python qa/site_e2e.py http://localhost:5173      # titles, recent plans, storage blocked, 404
uv run --with playwright python qa/journeys_e2e.py http://localhost:5173 qa/screenshots path/to/axe.min.js
                                                                          # full journeys, 390/768/1440 px, axe scan
uv run --with playwright python qa/a11y_probe.py http://localhost:5173    # contrast, focus, 200% zoom
python3 qa/api_fuzz.py http://127.0.0.1:8000/api                         # bad input → 4xx, never 500
```
`plan_e2e` and `site_e2e` use the demo plans (`uv run python -m scripts.seed_demo`). `journeys_e2e` takes the path to
`axe.min.js` from `npm i axe-core`. Set `CHROMIUM_PATH` to use a system Chromium instead of Playwright's.

## Deployment
Production runs behind **nginx** on a single Linux host. Reference configs are in [`deploy/`](deploy):
- nginx serves the built frontend (`frontend/deploy.sh` builds and syncs it to the web root, with an SPA fallback)
  and proxies `/api/` to uvicorn on `127.0.0.1:8000`;
- `POST /api/plans` is rate-limited per client IP (10/min, burst 5, JSON 429); API bodies are capped at 16 kB;
  the real client IP is trusted only from the upstream TLS proxy;
- the API runs as a **systemd** service (`launchwise-api.service`, 2 uvicorn workers, restart on failure);
- hashed assets are cached for a year, `index.html` is never cached.

## Project structure
```
launchwise/
├── backend/
│   ├── app/            FastAPI app: main.py, rules.py (engine), schemas.py, catalog.py, export.py,
│   │                   routers/ (options, plans, examples), services/freeserp.py
│   ├── scripts/        seed_demo.py
│   ├── sql/            001_create_plans.sql
│   └── tests/          pytest suite
├── frontend/
│   ├── src/            pages/, components/ (plan/, planner/), lib/, api.ts
│   └── public/         favicon, Open Graph image
├── qa/                 Playwright end-to-end, accessibility and API checks
├── deploy/             nginx and systemd reference configs
├── docs/screenshots/   images used in this README
├── docker-compose.yml  local MariaDB
└── .env.example
```

## Known limitations
- No accounts: a plan is private to whoever has its link; recent plans live only in the browser.
- Rule-based by design: predictable and explainable, but limited to seven business types.
- The rate limit is per IP, so users behind one shared IP share it.
- If the API is down, direct `/api/*` requests get nginx's HTML 502 page (the app itself shows a friendly message).

## License
[MIT](LICENSE) © 2026 Roman Nazarchuk
