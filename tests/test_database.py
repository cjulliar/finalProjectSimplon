"""
Tests pour les fonctionnalités de base de données.
"""
import os
import sys
import pytest
from pathlib import Path
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.database import Base
from src.db.models import BankData, User
from src.api.auth import get_password_hash


# Créer une base de données en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def setup_test_db():
    """Créer et initialiser une base de données de test."""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Créer une session
    db = TestingSessionLocal()
    
    yield db
    
    # Nettoyer
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_bank_data(setup_test_db):
    """Tester la création d'une entrée BankData."""
    db = setup_test_db
    
    # Créer une entrée BankData
    bank_data = BankData(
        agence="Agence Test",
        date=date.today(),
        montant=1000.0,
        nombre_transactions=10
    )
    
    # Ajouter à la base de données
    db.add(bank_data)
    db.commit()
    db.refresh(bank_data)
    
    # Vérifier l'ID
    assert bank_data.id is not None, "L'ID ne devrait pas être None après commit"
    
    # Vérifier les données
    assert bank_data.agence == "Agence Test"
    assert bank_data.date == date.today()
    assert bank_data.montant == 1000.0
    assert bank_data.nombre_transactions == 10
    assert bank_data.created_at is not None


def test_query_bank_data(setup_test_db):
    """Tester la récupération des données bancaires."""
    db = setup_test_db
    
    # Ajouter plusieurs entrées
    today = date.today()
    bank_data_entries = [
        BankData(agence="Agence A", date=today - timedelta(days=2), montant=1000.0, nombre_transactions=10),
        BankData(agence="Agence B", date=today - timedelta(days=1), montant=2000.0, nombre_transactions=20),
        BankData(agence="Agence A", date=today, montant=1500.0, nombre_transactions=15)
    ]
    
    db.add_all(bank_data_entries)
    db.commit()
    
    # Récupérer toutes les entrées
    all_data = db.query(BankData).all()
    assert len(all_data) == 3
    
    # Filtrer par agence
    agence_a_data = db.query(BankData).filter(BankData.agence == "Agence A").all()
    assert len(agence_a_data) == 2
    
    # Filtrer par date
    today_data = db.query(BankData).filter(BankData.date == today).all()
    assert len(today_data) == 1
    assert today_data[0].agence == "Agence A"
    assert today_data[0].montant == 1500.0


def test_update_bank_data(setup_test_db):
    """Tester la mise à jour des données bancaires."""
    db = setup_test_db
    
    # Créer une entrée
    bank_data = BankData(
        agence="Agence Test",
        date=date.today(),
        montant=1000.0,
        nombre_transactions=10
    )
    db.add(bank_data)
    db.commit()
    
    # Récupérer l'ID
    bank_data_id = bank_data.id
    
    # Modifier les données
    db_bank_data = db.query(BankData).filter(BankData.id == bank_data_id).first()
    db_bank_data.montant = 1500.0
    db_bank_data.nombre_transactions = 15
    db.commit()
    
    # Vérifier les modifications
    updated_data = db.query(BankData).filter(BankData.id == bank_data_id).first()
    assert updated_data.montant == 1500.0
    assert updated_data.nombre_transactions == 15


def test_delete_bank_data(setup_test_db):
    """Tester la suppression des données bancaires."""
    db = setup_test_db
    
    # Créer une entrée
    bank_data = BankData(
        agence="Agence Test",
        date=date.today(),
        montant=1000.0,
        nombre_transactions=10
    )
    db.add(bank_data)
    db.commit()
    
    # Récupérer l'ID
    bank_data_id = bank_data.id
    
    # Supprimer l'entrée
    db.delete(bank_data)
    db.commit()
    
    # Vérifier que l'entrée n'existe plus
    deleted_data = db.query(BankData).filter(BankData.id == bank_data_id).first()
    assert deleted_data is None


def test_create_user(setup_test_db):
    """Tester la création d'un utilisateur."""
    db = setup_test_db
    
    # Créer un utilisateur
    hashed_password = get_password_hash("password123")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    
    # Ajouter à la base de données
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Vérifier l'ID
    assert user.id is not None
    
    # Vérifier les données
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == hashed_password
    assert user.is_active is True
    assert user.created_at is not None


def test_user_unique_constraints(setup_test_db):
    """Tester les contraintes d'unicité pour l'utilisateur."""
    db = setup_test_db
    
    # Créer un premier utilisateur
    hashed_password = get_password_hash("password123")
    user1 = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user1)
    db.commit()
    
    # Tenter de créer un utilisateur avec le même nom d'utilisateur
    user2 = User(
        username="testuser",  # Même username
        email="autre@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user2)
    
    # Vérifier que cela génère une erreur
    with pytest.raises(IntegrityError):
        db.commit()
    
    # Rollback pour nettoyer la session
    db.rollback()
    
    # Tenter de créer un utilisateur avec le même email
    user3 = User(
        username="autreuser",
        email="test@example.com",  # Même email
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user3)
    
    # Vérifier que cela génère une erreur
    with pytest.raises(IntegrityError):
        db.commit() 