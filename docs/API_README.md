# Documentation de l'API Rapports Bancaires

## Introduction

Cette API permet d'accéder aux données bancaires stockées dans la base de données. Elle utilise FastAPI avec authentification OAuth2 (JWT) pour sécuriser l'accès aux données.

## Configuration

### Prérequis

- Python 3.10 ou supérieur
- FastAPI
- SQLAlchemy
- Uvicorn

### Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Créer un utilisateur administrateur :
```bash
python3.10 src/scripts/create_admin.py --username admin --password votremotdepasse --email admin@example.com
```

3. Lancer l'API :
```bash
python3.10 src/scripts/run_api.py --reload
```

## Points de terminaison (Endpoints)

### Authentification

#### Obtenir un token d'accès

```
POST /api/token
```

**Paramètres de formulaire :**
- `username` (obligatoire) : Nom d'utilisateur
- `password` (obligatoire) : Mot de passe

**Réponse :**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Utilisateurs

#### Créer un utilisateur

```
POST /api/users
```

**Corps de la requête :**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "is_active": true
}
```

**Réponse :**
```json
{
  "username": "string",
  "email": "string",
  "is_active": true,
  "id": 0
}
```

#### Obtenir les informations de l'utilisateur connecté

```
GET /api/users/me
```

**En-têtes :**
- `Authorization: Bearer {token}`

**Réponse :**
```json
{
  "username": "string",
  "email": "string",
  "is_active": true,
  "id": 0
}
```

### Données bancaires

#### Récupérer toutes les données bancaires

```
GET /api/bank-data
```

**En-têtes :**
- `Authorization: Bearer {token}`

**Paramètres de requête :**
- `skip` (optionnel) : Nombre d'éléments à sauter (pagination)
- `limit` (optionnel) : Nombre maximum d'éléments à retourner
- `agence` (optionnel) : Filtrer par nom d'agence
- `date_debut` (optionnel) : Filtrer à partir de cette date (format ISO 8601)
- `date_fin` (optionnel) : Filtrer jusqu'à cette date (format ISO 8601)

**Réponse :**
```json
[
  {
    "agence": "string",
    "date": "2023-01-01",
    "montant": 0,
    "nombre_transactions": 0,
    "id": 0,
    "created_at": "2023-01-01T12:00:00.000Z"
  }
]
```

#### Récupérer une entrée par ID

```
GET /api/bank-data/{bank_data_id}
```

**En-têtes :**
- `Authorization: Bearer {token}`

**Paramètres de chemin :**
- `bank_data_id` (obligatoire) : ID de l'entrée à récupérer

**Réponse :**
```json
{
  "agence": "string",
  "date": "2023-01-01",
  "montant": 0,
  "nombre_transactions": 0,
  "id": 0,
  "created_at": "2023-01-01T12:00:00.000Z"
}
```

#### Créer une nouvelle entrée

```
POST /api/bank-data
```

**En-têtes :**
- `Authorization: Bearer {token}`

**Corps de la requête :**
```json
{
  "agence": "string",
  "date": "2023-01-01",
  "montant": 0,
  "nombre_transactions": 0
}
```

**Réponse :**
```json
{
  "agence": "string",
  "date": "2023-01-01",
  "montant": 0,
  "nombre_transactions": 0,
  "id": 0,
  "created_at": "2023-01-01T12:00:00.000Z"
}
```

### Statistiques

#### Obtenir des statistiques par agence

```
GET /api/bank-data/stats/by-agence
```

**En-têtes :**
- `Authorization: Bearer {token}`

**Réponse :**
```json
[
  {
    "agence": "string",
    "montant_total": 0,
    "transactions_total": 0,
    "nombre_entrees": 0
  }
]
```

#### Obtenir des statistiques par date

```
GET /api/bank-data/stats/by-date
```

**En-têtes :**
- `Authorization: Bearer {token}`

**Paramètres de requête :**
- `days` (optionnel) : Nombre de jours à analyser (par défaut: 30)

**Réponse :**
```json
[
  {
    "date": "2023-01-01",
    "montant_total": 0,
    "transactions_total": 0,
    "nombre_entrees": 0
  }
]
```

## Sécurité

L'API utilise OAuth2 avec des tokens JWT pour sécuriser l'accès aux données. Tous les points de terminaison, à l'exception de la route d'authentification (/api/token) et de création d'utilisateur (/api/users), nécessitent un token d'accès valide.

### Obtenir un token

1. Appelez le point de terminaison POST /api/token avec vos identifiants
2. Récupérez le token JWT retourné
3. Incluez ce token dans l'en-tête Authorization pour les requêtes ultérieures

## Documentation interactive

L'API propose deux interfaces de documentation interactive :

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

Ces interfaces permettent d'explorer et de tester l'API directement depuis votre navigateur.

## Exemples d'utilisation avec curl

### Obtenir un token

```bash
curl -X POST "http://localhost:8000/api/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=votremotdepasse"
```

### Récupérer toutes les données bancaires

```bash
curl -X GET "http://localhost:8000/api/bank-data" -H "Authorization: Bearer {votre_token}"
```

### Récupérer les données bancaires pour une agence spécifique

```bash
curl -X GET "http://localhost:8000/api/bank-data?agence=Agence1" -H "Authorization: Bearer {votre_token}"
```

### Créer une nouvelle entrée

```bash
curl -X POST "http://localhost:8000/api/bank-data" -H "Authorization: Bearer {votre_token}" -H "Content-Type: application/json" -d '{"agence": "NouvelleAgence", "date": "2023-05-01", "montant": 5000, "nombre_transactions": 50}'
```

## Intégration avec d'autres applications

L'API peut être facilement intégrée à d'autres applications en utilisant des bibliothèques HTTP standard. Voici un exemple avec Python et la bibliothèque `requests` :

```python
import requests

# Authentification
response = requests.post(
    "http://localhost:8000/api/token",
    data={"username": "admin", "password": "votremotdepasse"}
)
token = response.json()["access_token"]

# Récupérer les données
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/bank-data", headers=headers)
data = response.json()

# Utiliser les données
for item in data:
    print(f"Agence: {item['agence']}, Montant: {item['montant']}") 