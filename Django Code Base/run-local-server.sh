# Run local server for development

set -e

echo "[1/3] Loading environment variables from .env (if present)..."
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo ".env loaded."
else
  echo "No .env file found. Make sure environment variables are set."
fi

echo "[2/3] Applying Django migrations..."
python manage.py migrate

echo "[3/3] Starting Django development server..."
python manage.py runserver 
# Run local server for development

set -e

echo "[1/3] Loading environment variables from .env (if present)..."
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo ".env loaded."
else
  echo "No .env file found. Make sure environment variables are set."
fi

echo "[2/3] Applying Django migrations..."
python manage.py migrate

echo "[3/3] Starting Django development server..."
python manage.py runserver 