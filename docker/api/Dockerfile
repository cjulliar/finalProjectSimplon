FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ ./src/

# Exposition du port
EXPOSE 8000

# Point d'entrée
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 