# FourFrame — House Hunting App

A Flask backend (JWT auth) + a plain HTML/CSS/JS frontend. Users register/login, then
logged-in users can post houses; anyone can browse listings.

## What was added to your backend

- **`app/models.py`** — new `House` model (title, description, price, location, bedrooms,
  bathrooms, house_type, listing_type, image_url, contact_phone, owner_id) linked to `User`.
- **`app/routes.py`** — new endpoints:
  - `GET  /api/houses`        — public, browse all listings (supports `?location=&listing_type=&min_price=&max_price=`)
  - `GET  /api/houses/<id>`   — public, single listing
  - `GET  /api/houses/mine`   — auth required, current user's listings
  - `POST /api/houses`        — auth required, post a new house
  - `PUT  /api/houses/<id>`   — auth required, edit your own listing
  - `DELETE /api/houses/<id>` — auth required, delete your own listing
  - Also fixed a bug: `flask-jwt-extended` requires the JWT `identity` to be a string —
    the existing register/login/refresh routes were passing the raw integer `user.id`,
    which throws `"Subject must be a string"` the moment a protected route is hit.
    All three now pass `str(user.id)`.

# FourFrame — House Hunting App

A Flask backend (JWT auth) + a plain HTML/CSS/JS frontend. Users register/login, then
logged-in users can post houses; anyone can browse listings.

## Quick start (recommended)

Everything is pre-configured — just run one script:

```bash
./start.sh
```

This will (safe to re-run any time):
- create a Python virtual environment inside `project/` if it doesn't exist yet
- install backend dependencies
- create the SQLite database tables if they don't exist yet
- start the backend on `http://localhost:5000`
- start the frontend on `http://localhost:3000`

Then just open **http://localhost:3000** in your browser. Press `Ctrl+C` in the
terminal to stop both servers.

If `./start.sh` says "permission denied", run `chmod +x start.sh` once first.

A working `.env` (with a real JWT secret already filled in) ships in `project/.env`,
so there's no manual setup needed for local use. If you ever want a different secret,
edit `project/.env` — `JWT_SECRET_KEY` can be any long random string.

## What was added to your backend

- **`app/models.py`** — new `House` model (title, description, price, location, bedrooms,
  bathrooms, house_type, listing_type, image_url, contact_phone, owner_id) linked to `User`.
- **`app/routes.py`** — new endpoints:
  - `GET  /api/houses`        — public, browse all listings (supports `?location=&listing_type=&min_price=&max_price=`)
  - `GET  /api/houses/<id>`   — public, single listing
  - `GET  /api/houses/mine`   — auth required, current user's listings
  - `POST /api/houses`        — auth required, post a new house
  - `PUT  /api/houses/<id>`   — auth required, edit your own listing
  - `DELETE /api/houses/<id>` — auth required, delete your own listing
  - Also fixed a bug: `flask-jwt-extended` requires the JWT `identity` to be a string —
    the existing register/login/refresh routes were passing the raw integer `user.id`,
    which throws `"Subject must be a string"` the moment a protected route is hit.
    All three now pass `str(user.id)`.

## Manual setup (if you don't want to use start.sh)

```bash
cd project
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# .env is already included with a working JWT secret and FRONTEND_URL=http://localhost:3000
export $(cat .env | xargs)

# create the database tables (SQLite by default, saved to project/instance/app.db)
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

python3 run.py
```

In a second terminal:
```bash
cd frontend
python3 -m http.server 3000
```

`frontend/index.html` is a single self-contained file — it talks to the backend at
`http://localhost:5000/api` by default. Change the `API_BASE` constant near the top of
the `<script>` block in `index.html` if you run the backend somewhere else.

## How it works for the user

1. **Register** → creates an account and logs you straight in.
2. **Login** → existing users sign in.
3. Once logged in, the nav bar shows **Post a house** and **My listings**.
4. **Post a house** → fills out title/price/location/etc. and submits — this becomes
   visible to everyone under **Browse**.
5. **Browse** → open to everyone, no login required, with filters by location, type
   (rent/sale), and price range.
6. **My listings** → shows only the listings you posted, with a delete option.

## Notes

- The frontend keeps the JWT access/refresh tokens in memory only (a JS variable) for
  the current page session — no `localStorage`, so nothing is left behind in the browser.
  If you want sessions to survive a page refresh, swap that for `localStorage` yourself.
- The `House.to_dict()` also returns `owner_name` so listing cards can show who posted
  a house without a second API call.
# House-Hunting-app
