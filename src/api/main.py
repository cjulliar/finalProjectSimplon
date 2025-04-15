"""
Module principal de l'API FastAPI.
"""
import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.api.models import BankDataResponse
from src.api.auth import get_current_user
from src.api.routes import router as api_router
from src.api.ia_routes import router as ia_router

# Créer l'application FastAPI
app = FastAPI(
    title="API Rapports Bancaires",
    description="API pour accéder aux données bancaires et à l'analyse par IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurer les CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes de l'API
app.include_router(api_router, prefix="/api", tags=["api"])

# Inclure les routes de l'IA
app.include_router(ia_router, prefix="/api", tags=["ai"])

@app.get("/")
async def root():
    """Route racine de l'API."""
    return {
        "message": "Bienvenue dans l'API Rapports Bancaires",
        "version": "1.0.0",
        "features": ["Données bancaires", "Analyse IA", "Rapports automatisés"],
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    """Vérifier l'état de santé de l'API."""
    return {"status": "ok"}

# Pour démarrer l'API en local : uvicorn src.api.main:app --reload 