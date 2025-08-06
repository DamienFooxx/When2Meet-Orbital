# Run local server for development

set -e

echo "[1/2] Loading environment variables from .env (if present)..."
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo ".env loaded."
else
  echo "No .env file found. Make sure environment variables are set."
fi

echo "[2/2] Applying Django migrations..."
python manage.py makemigrations
python manage.py migrate