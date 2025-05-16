from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime


class BankData(Base):
    """Modèle pour les données bancaires hebdomadaires"""
    __tablename__ = "bank_data"

    id = Column(Integer, primary_key=True, index=True)
    agence = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    montant = Column(Float, nullable=False)
    nombre_transactions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<BankData(agence='{self.agence}', date='{self.date}', montant={self.montant})>"


class BankDataRaw(Base):
    """Modèle pour les données bancaires brutes importées du fichier Excel"""
    __tablename__ = "bank_data_raw"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(String, index=True, nullable=False)  # ID_SEM_COMM
    group_name = Column(String, index=True, nullable=False)  # GROUPE
    bank_name = Column(String, index=True, nullable=False)  # MULTI_SITE
    raw_data = Column(JSON, nullable=False)  # Toutes les données brutes
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<BankDataRaw(week_id='{self.week_id}', group_name='{self.group_name}', bank_name='{self.bank_name}')>"


class User(Base):
    """Modèle pour les utilisateurs de l'API"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    # Relations
    analyses = relationship("Analysis", back_populates="user")
    schedules = relationship("ScheduledReport", back_populates="user")
    email_reports = relationship("EmailReport", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Analysis(Base):
    """Modèle pour les analyses générées par l'IA"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    query_parameters = Column(JSON, nullable=False)  # Paramètres de la requête
    report = Column(Text, nullable=False)  # Contenu du rapport
    analysis_metadata = Column(JSON, nullable=False)  # Métadonnées de l'analyse
    
    # Relations
    user = relationship("User", back_populates="analyses")
    visualizations = relationship("Visualization", back_populates="analysis")
    
    def __repr__(self):
        return f"<Analysis(id='{self.id}', user_id={self.user_id}, created_at='{self.created_at}')>"


class Visualization(Base):
    """Modèle pour les visualisations générées par l'IA"""
    __tablename__ = "visualizations"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    path = Column(String, nullable=False)  # Chemin du fichier
    title = Column(String, nullable=False)  # Titre de la visualisation
    type = Column(String, nullable=False)  # Type de visualisation (bar_chart, line_chart, etc.)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    # Relations
    analysis = relationship("Analysis", back_populates="visualizations")
    
    def __repr__(self):
        return f"<Visualization(id='{self.id}', analysis_id='{self.analysis_id}', title='{self.title}')>"


class ScheduledReport(Base):
    """Modèle pour les rapports planifiés"""
    __tablename__ = "scheduled_reports"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_type = Column(String, nullable=False)  # daily, weekly, monthly
    day = Column(Integer, nullable=False)  # jour de la semaine (0-6) ou du mois (1-31)
    recipients = Column(JSON, nullable=False)  # Liste des destinataires
    agence = Column(String, nullable=True)  # Agence à analyser (optionnel)
    include_visualizations = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    last_run = Column(DateTime, nullable=True)  # Dernière exécution
    
    # Relations
    user = relationship("User", back_populates="schedules")
    
    def __repr__(self):
        return f"<ScheduledReport(id='{self.id}', schedule_type='{self.schedule_type}', is_active={self.is_active})>"


class EmailReport(Base):
    """Modèle pour les rapports envoyés par email"""
    __tablename__ = "email_reports"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank_name = Column(String, index=True, nullable=False)  # Nom de la banque analysée
    subject = Column(String, nullable=False)  # Sujet de l'email
    recipients = Column(JSON, nullable=False)  # Liste des destinataires
    content = Column(Text, nullable=False)  # Contenu HTML de l'email
    sent_at = Column(DateTime, default=datetime.datetime.now)
    scheduled_report_id = Column(String, ForeignKey("scheduled_reports.id"), nullable=True)  # Lien vers le rapport planifié (si applicable)
    status = Column(String, default="sent")  # Status de l'email: sent, failed, etc.
    
    # Relations
    user = relationship("User", back_populates="email_reports")
    scheduled_report = relationship("ScheduledReport")
    
    def __repr__(self):
        return f"<EmailReport(id='{self.id}', bank_name='{self.bank_name}', sent_at='{self.sent_at}')>"


# Mise à jour des relations
User.scheduled_reports = relationship("ScheduledReport", back_populates="user") 