"""
Routes de l'API.
"""
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.database import get_db
from src.db.models import BankData, User
from src.api.models import BankDataResponse, BankDataCreate, UserResponse, UserCreate, Token
from src.api.auth import authenticate_user, create_access_token, get_current_user, get_password_hash

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Obtenir un token d'accès JWT."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Obtenir les informations de l'utilisateur connecté."""
    return current_user


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouvel utilisateur."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà utilisé")
    
    if user.email:
        db_email = db.query(User).filter(User.email == user.email).first()
        if db_email:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/bank-data", response_model=List[BankDataResponse])
async def read_bank_data(
    skip: int = 0,
    limit: int = 100,
    agence: Optional[str] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer les données bancaires.
    
    - **skip**: Nombre d'éléments à sauter (pagination)
    - **limit**: Nombre maximum d'éléments à retourner
    - **agence**: Filtrer par nom d'agence
    - **date_debut**: Filtrer à partir de cette date
    - **date_fin**: Filtrer jusqu'à cette date
    """
    query = db.query(BankData)
    
    # Appliquer les filtres
    if agence:
        query = query.filter(BankData.agence == agence)
    if date_debut:
        query = query.filter(BankData.date >= date_debut)
    if date_fin:
        query = query.filter(BankData.date <= date_fin)
    
    # Appliquer la pagination
    bank_data = query.offset(skip).limit(limit).all()
    return bank_data


@router.get("/bank-data/{bank_data_id}", response_model=BankDataResponse)
async def read_bank_data_by_id(
    bank_data_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer une entrée de données bancaires par son ID.
    
    - **bank_data_id**: ID de l'entrée à récupérer
    """
    bank_data = db.query(BankData).filter(BankData.id == bank_data_id).first()
    if bank_data is None:
        raise HTTPException(status_code=404, detail="Données non trouvées")
    return bank_data


@router.post("/bank-data", response_model=BankDataResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_data(
    bank_data: BankDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle entrée de données bancaires.
    
    - **bank_data**: Données bancaires à créer
    """
    db_bank_data = BankData(
        agence=bank_data.agence,
        date=bank_data.date,
        montant=bank_data.montant,
        nombre_transactions=bank_data.nombre_transactions
    )
    db.add(db_bank_data)
    db.commit()
    db.refresh(db_bank_data)
    return db_bank_data


@router.get("/bank-data/stats/by-agence", response_model=List[dict])
async def get_bank_data_stats_by_agence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir des statistiques par agence (montant total, nombre de transactions).
    """
    stats = db.query(
        BankData.agence,
        func.sum(BankData.montant).label("montant_total"),
        func.sum(BankData.nombre_transactions).label("transactions_total"),
        func.count(BankData.id).label("nombre_entrees")
    ).group_by(BankData.agence).all()
    
    result = [
        {
            "agence": row.agence,
            "montant_total": row.montant_total,
            "transactions_total": row.transactions_total,
            "nombre_entrees": row.nombre_entrees
        }
        for row in stats
    ]
    return result


@router.get("/bank-data/stats/by-date", response_model=List[dict])
async def get_bank_data_stats_by_date(
    days: int = Query(30, description="Nombre de jours à analyser, par défaut 30"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir des statistiques par date (montant total, nombre de transactions).
    
    - **days**: Nombre de jours à analyser (par défaut: 30 derniers jours)
    """
    date_limite = date.today() - timedelta(days=days)
    
    stats = db.query(
        BankData.date,
        func.sum(BankData.montant).label("montant_total"),
        func.sum(BankData.nombre_transactions).label("transactions_total"),
        func.count(BankData.id).label("nombre_entrees")
    ).filter(
        BankData.date >= date_limite
    ).group_by(BankData.date).order_by(BankData.date).all()
    
    result = [
        {
            "date": row.date.isoformat(),
            "montant_total": row.montant_total,
            "transactions_total": row.transactions_total,
            "nombre_entrees": row.nombre_entrees
        }
        for row in stats
    ]
    return result 