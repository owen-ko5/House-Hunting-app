#!/usr/bin/env bash
# FourFrame — one-command start for backend + frontend.
# Usage: ./start.sh   (from the project root, i.e. the folder this file is in)

set -e
cd "$(dirname "$0")"

echo "== FourFrame setup =="

# ---- backend setup ----
cd project

if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "Installing backend dependencies..."
./venv/bin/pip install -q --disable-pip-version-check -r requirements.txt

echo "Ensuring database tables exist..."
set -a
source .env
set +a
./venv/bin/python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo "Starting backend on http://localhost:5000 ..."
./venv/bin/python3 run.py > ../backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# ---- frontend setup ----
echo "Starting frontend on http://localhost:3000 ..."
cd frontend
python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================================"
echo " Backend:  http://localhost:5000/api"
echo " Frontend: http://localhost:3000"
echo ""
echo " Open http://localhost:3000 in your browser."
echo " Press Ctrl+C to stop both servers."
echo "======================================================"

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

wait
