# 1️⃣ Image de base Python
FROM python:3.12-slim

# 2️⃣ Définir le répertoire de travail
WORKDIR /app

# 3️⃣ Copier uniquement le fichier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copier tout le reste du projet (sauf ce qui est ignoré)
COPY . .

# 5️⃣ Exposer le port FastAPI
EXPOSE 8000

# 6️⃣ Commande pour lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
