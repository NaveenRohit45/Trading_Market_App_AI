FROM python:3.12-slim

WORKDIR /app

# System deps needed by some packages (pandas/numpy build chains etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# data/ holds the SQLite DB and models/ holds trained ML artifacts --
# persist these as a volume in docker-compose.yml, don't bake them
# into the image.
RUN mkdir -p /app/data /app/models

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
