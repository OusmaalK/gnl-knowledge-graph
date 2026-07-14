# Utiliser une image Node.js
FROM node:20-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances sans verrouillage strict
RUN npm install --legacy-peer-deps

# Copier tout le code
COPY . .

# Exposer le port
EXPOSE 3000

# Lancer l'application en mode développement (Pas de build statique)
CMD ["npm", "run", "dev"]