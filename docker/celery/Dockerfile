FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Installer le package en mode développement
RUN pip install -e .

# Créer le répertoire output s'il n'existe pas
RUN mkdir -p /app/output

# Définir les variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV CELERY_APP=src.celery_app

# Commande par défaut pour le worker
CMD ["celery", "-A", "src.celery_app", "worker", "--loglevel=info", "--concurrency=2"] 