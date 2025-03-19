"""
Tests pour la base de données.
"""
import os
import sys
import time
import pytest
import pandas as pd
from pathlib import Path
from datetime import date

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.database import engine, Base, SessionLocal
from src.db.models import BankData


@pytest.fixture(scope="function")
def setup_test_db():
    """Configure une base de données de test temporaire."""
    # Créer les tables dans la base de données
    Base.metadata.create_all(bind=engine)
    
    # Fournir une session de base de données
    db = SessionLocal()
    
    try:
        yield db
    finally:
        # Nettoyer après le test
        db.close()
        # Supprimer toutes les tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_bank_data():
    """Crée des données bancaires de test."""
    return [
        BankData(agence="Agence1", date=date(2023, 1, 1), montant=1000.50, nombre_transactions=5),
        BankData(agence="Agence2", date=date(2023, 1, 2), montant=2500.75, nombre_transactions=10),
        BankData(agence="Agence3", date=date(2023, 1, 3), montant=750.25, nombre_transactions=3),
    ]


def test_database_connection():
    """Teste la connexion à la base de données."""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Vérifier que la connexion fonctionne
    db = SessionLocal()
    assert db is not None
    db.close()
    
    # Nettoyer
    Base.metadata.drop_all(bind=engine)


def test_create_bank_data(setup_test_db):
    """Teste la création d'une entrée BankData."""
    db = setup_test_db
    
    # Créer une entrée
    bank_data = BankData(
        agence="TestAgence",
        date=date(2023, 1, 1),
        montant=1000.0,
        nombre_transactions=5
    )
    
    # Ajouter et valider
    db.add(bank_data)
    db.commit()
    db.refresh(bank_data)
    
    # Vérifier l'ID (doit être > 0)
    assert bank_data.id > 0
    
    # Vérifier les valeurs
    assert bank_data.agence == "TestAgence"
    assert bank_data.date == date(2023, 1, 1)
    assert bank_data.montant == 1000.0
    assert bank_data.nombre_transactions == 5
    assert bank_data.created_at is not None


def test_read_bank_data(setup_test_db, sample_bank_data):
    """Teste la lecture des entrées BankData."""
    db = setup_test_db
    
    # Ajouter des entrées
    for data in sample_bank_data:
        db.add(data)
    db.commit()
    
    # Lire les entrées
    all_data = db.query(BankData).all()
    
    # Vérification
    assert len(all_data) == 3
    assert all_data[0].agence == "Agence1"
    assert all_data[1].agence == "Agence2"
    assert all_data[2].agence == "Agence3"


def test_update_bank_data(setup_test_db, sample_bank_data):
    """Teste la mise à jour d'une entrée BankData."""
    db = setup_test_db
    
    # Ajouter des entrées
    for data in sample_bank_data:
        db.add(data)
    db.commit()
    
    # Récupérer la première entrée
    data = db.query(BankData).first()
    
    # Mettre à jour
    data.montant = 1500.0
    db.commit()
    db.refresh(data)
    
    # Vérification
    assert data.montant == 1500.0


def test_delete_bank_data(setup_test_db, sample_bank_data):
    """Teste la suppression d'une entrée BankData."""
    db = setup_test_db
    
    # Ajouter des entrées
    for data in sample_bank_data:
        db.add(data)
    db.commit()
    
    # Récupérer la première entrée
    data = db.query(BankData).first()
    
    # Supprimer
    db.delete(data)
    db.commit()
    
    # Vérification
    all_data = db.query(BankData).all()
    assert len(all_data) == 2


def test_filter_by_agence(setup_test_db, sample_bank_data):
    """Teste le filtrage par agence."""
    db = setup_test_db
    
    # Ajouter des entrées
    for data in sample_bank_data:
        db.add(data)
    db.commit()
    
    # Filtrer par agence
    agence1_data = db.query(BankData).filter(BankData.agence == "Agence1").all()
    
    # Vérification
    assert len(agence1_data) == 1
    assert agence1_data[0].agence == "Agence1"


def test_filter_by_date(setup_test_db, sample_bank_data):
    """Teste le filtrage par date."""
    db = setup_test_db
    
    # Ajouter des entrées
    for data in sample_bank_data:
        db.add(data)
    db.commit()
    
    # Filtrer par date
    date_data = db.query(BankData).filter(BankData.date == date(2023, 1, 1)).all()
    
    # Vérification
    assert len(date_data) == 1
    assert date_data[0].date == date(2023, 1, 1)


def test_performance_batch_insert(setup_test_db):
    """Teste les performances d'insertion par lots."""
    db = setup_test_db
    
    # Nombre d'entrées à insérer
    n_entries = 1000
    
    # Créer les données
    data = []
    for i in range(n_entries):
        data.append(BankData(
            agence=f"Agence{i % 10}",
            date=date(2023, 1, 1 + i % 31),
            montant=1000.0 + i,
            nombre_transactions=5 + i % 20
        ))
    
    # Mesurer le temps d'insertion
    start_time = time.time()
    
    # Insérer par lots
    batch_size = 100
    for i in range(0, n_entries, batch_size):
        batch = data[i:i+batch_size]
        db.add_all(batch)
        db.commit()
    
    end_time = time.time()
    
    # Vérification
    all_data = db.query(BankData).all()
    assert len(all_data) == n_entries
    
    # Afficher les performances
    print(f"Temps d'insertion de {n_entries} entrées par lots: {end_time - start_time:.2f} secondes")


def test_count_rows(setup_test_db, sample_bank_data):
    """Teste le comptage de lignes dans la base de données."""
    db = setup_test_db
    
    # Ajouter des entrées
    for data in sample_bank_data:
        db.add(data)
    db.commit()
    
    # Compter les lignes
    count = db.query(BankData).count()
    
    # Vérification
    assert count == 3 