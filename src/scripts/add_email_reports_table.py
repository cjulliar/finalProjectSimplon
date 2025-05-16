#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour ajouter directement la table email_reports à la base de données.
Ce script contourne le système de migration Alembic pour résoudre les problèmes
de migration.
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.exc import SQLAlchemyError

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = os.environ.get("DB_PATH", "bankreports.db")
DATABASE_URL = f"sqlite:///./{DB_PATH}"

def create_email_reports_table():
    """
    Crée la table email_reports dans la base de données si elle n'existe pas déjà.
    """
    try:
        # Connexion à la base de données
        logger.info(f"Utilisation de SQLite: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        metadata = MetaData()
        
        # Vérification si la table existe déjà
        inspector = engine.dialect.has_table(engine.connect(), "email_reports")
        if inspector:
            logger.info("La table email_reports existe déjà.")
            return True
        
        # Définition de la table email_reports
        email_reports = Table(
            'email_reports', 
            metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, nullable=True),
            Column('bank_name', String(255), nullable=False),
            Column('subject', String(255), nullable=False),
            Column('recipients', String(1024), nullable=False),
            Column('content', Text, nullable=False),
            Column('sent_at', DateTime, default=datetime.utcnow),
            Column('scheduled_report_id', Integer, nullable=True),
            Column('status', String(50), nullable=False, default='sent')
        )
        
        # Création de la table
        metadata.create_all(engine, tables=[email_reports])
        logger.info("Table email_reports créée avec succès.")
        return True
    
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la création de la table email_reports: {e}")
        return False

if __name__ == "__main__":
    logger.info("Début de la création de la table email_reports...")
    success = create_email_reports_table()
    
    if success:
        logger.info("Opération terminée avec succès.")
        sys.exit(0)
    else:
        logger.error("Échec de l'opération.")
        sys.exit(1) 