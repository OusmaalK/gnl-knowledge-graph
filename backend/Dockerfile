# Utiliser une image Python légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances de PRODUCTION
COPY requirements-docker.txt .
# Installer les dépendances
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier tout le reste du code
COPY . .

# Exposer le port de l'API
EXPOSE 8000

# Lancer l'application
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]