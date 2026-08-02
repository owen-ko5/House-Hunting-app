# FourFrame — House Hunting App

[![CI](https://github.com/owen-ko5/House-Hunting-app/actions/workflows/ci.yml/badge.svg)](https://github.com/owen-ko5/House-Hunting-app/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Find your 4 walls today. A Flask + JWT backend and a static HTML/CSS/JS frontend for
posting and browsing house listings.

**Live:** [house-hunting-app-beta.vercel.app](https://house-hunting-app-beta.vercel.app/)

## Features

- Email/password auth with short-lived access tokens + refresh tokens
- Post, edit, and delete your own listings; browse everyone else's
- Filter listings by location, type (rent/sale), and price range, with pagination
- Direct-to-Cloudinary image uploads from the browser
- Rate limiting on auth endpoints, structured logging, JSON error responses, and
  optional Sentry error tracking — see [Production hardening](#production-hardening)

## Quick start (local dev)

**Option A — Docker (recommended, no local Python/Postgres setup needed):**

```bash
docker compose up --build
```

Then open **http://localhost:3000**. This starts Postgres, the API on `:5000`,
and the static frontend on `:3000`, wired together automatically.

**Option B — native, via the helper script:**

```bash
./start.sh
```

This creates a venv in `project/`, installs dependencies, creates SQLite tables,
and starts the backend (`:5000`) and frontend (`:3000`). Re-running it is safe.
If you get "permission denied", run `chmod +x start.sh` once first.

Before running natively, copy the env template and set your own secret:

```bash
cp project/.env.example project/.env
# edit project/.env and set JWT_SECRET_KEY to a long random string
```

**Option C — fully manual:**

```bash
cd project
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit JWT_SECRET_KEY
export $(cat .env | xargs)
flask db upgrade        # or: python3 -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
python3 run.py
```

In a second terminal:

```bash
cd frontend && python3 -m http.server 3000
```

`frontend/index.html` is a single self-contained file. Change the `API_BASE`
constant near the top of the `<script>` block if your backend runs elsewhere.

## API

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| POST | `/api/register` | – | rate-limited (10/hr per IP) |
| POST | `/api/login` | – | rate-limited (10/min per IP) |
| POST | `/api/refresh` | – | exchange a refresh token for a new access token |
| POST | `/api/logout` | ✓ | revokes the given refresh token |
| GET | `/api/profile` | ✓ | |
| PUT | `/api/profile` | ✓ | |
| GET | `/api/houses` | – | `?location=&listing_type=&min_price=&max_price=&page=&per_page=` |
| GET | `/api/houses/mine` | ✓ | |
| GET/POST/PUT/DELETE | `/api/houses/<id>` | GET public, others ✓ + ownership check |
| GET | `/api/health` | – | liveness check |

`GET /api/houses` returns `{ houses, page, per_page, total, total_pages }`.

## Production hardening

Added on top of the original MVP:

- **Rate limiting** (`flask-limiter`) on `/register` and `/login` to slow down
  brute-force/credential-stuffing attempts. Uses in-memory storage by default —
  set `RATELIMIT_STORAGE_URI` to a Redis URL if you run more than one instance.
- **Pagination** on `GET /api/houses` so the endpoint stays fast as listings grow.
- **Global JSON error handlers** — unexpected exceptions never leak stack traces
  to clients; they're logged server-side instead.
- **Security headers** (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, HSTS in production) on every response.
- **Structured stdout logging** — plays nicely with Render/Heroku/Docker log
  collection out of the box.
- **Optional Sentry integration** — set `SENTRY_DSN` to get error alerts; the app
  runs fine without it.
- **Docker + docker-compose** for a reproducible local environment matching
  what runs in Docker-based production deploys.
- **CI** (`.github/workflows/ci.yml`) — lints and runs the test suite on every
  push/PR.
- **Test suite** (`project/tests/`) covering auth, listing CRUD, and ownership
  checks — run with `pytest -q` from `project/`.

## Environment variables

See [`project/.env.example`](./project/.env.example) for the full list.
Required: `JWT_SECRET_KEY`, `DATABASE_URL`. Optional: `FRONTEND_URL`,
`SENTRY_DSN`, `LOG_LEVEL`, `RATELIMIT_STORAGE_URI`.

**Never commit `.env`.** It's gitignored; only `.env.example` (with placeholder
values) is checked in.

## Deploying

The app already targets a split deploy:

- **Backend** → Render (or any host that runs `gunicorn`). `Procfile` runs
  `flask db upgrade && gunicorn run:app`. Set `DATABASE_URL` to a managed
  Postgres instance, and set `JWT_SECRET_KEY`/`FRONTEND_URL`/`SENTRY_DSN` in
  the platform's environment settings — never in code.
- **Frontend** → Vercel (static hosting of `frontend/index.html`). Update
  `API_BASE` in `index.html` to point at your backend URL.

## How it works for the user

1. **Register** → creates an account and logs you straight in.
2. **Login** → existing users sign in.
3. Once logged in, the nav bar shows **Post a house** and **My listings**.
4. **Post a house** → fills out title/price/location/etc., uploads an image
   directly to Cloudinary, and submits — visible to everyone under **Browse**.
5. **Browse** → open to everyone, no login required, with filters and
   "Load more" pagination.
6. **My listings** → shows only the listings you posted, with a delete option.

## Notes

- Access/refresh tokens are kept in a JS variable, not `localStorage` — nothing
  persists in the browser, but sessions don't survive a page refresh by design.
  Swap in `localStorage` (with appropriate XSS precautions) if you want that.
- `House.to_dict()` includes `owner_name` so listing cards avoid a second API call.

## Roadmap (not yet implemented)

These matter for real public/mass-scale use and are the natural next steps:

- Email verification and password reset flow
- Listing moderation / reporting (spam, fraud, duplicate posts)
- Server-side image validation (size/type limits) beyond the client-side
  Cloudinary widget
- A proper frontend build (the single-file HTML approach will get hard to
  maintain past a certain size)
- Privacy policy / terms of service before onboarding real users
