#!/usr/bin/env python3
"""
Script pour vérifier les données dans la base de données.
"""
import sys
from pathlib import Path
import json

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent))

from src.db.database import get_db, engine
from src.db.models import BankData, BankDataRaw
from sqlalchemy.orm import Session

def main():
    """Point d'entrée principal."""
    # Vérifier les données BankData
    db = Session(engine)
    try:
        bank_data = db.query(BankData).all()
        print(f"BankData: {len(bank_data)} enregistrements")
        if bank_data:
            print(f"Premier enregistrement BankData: {bank_data[0].id}, {bank_data[0].date}")
    except Exception as e:
        print(f"Erreur lors de la vérification de BankData: {str(e)}")
    finally:
        db.close()
    
    # Vérifier les données BankDataRaw
    db = Session(engine)
    try:
        try:
            raw_data = db.query(BankDataRaw).all()
            print(f"BankDataRaw: {len(raw_data)} enregistrements")
            if raw_data:
                print(f"Premier enregistrement BankDataRaw: {raw_data[0].bank_name}, {raw_data[0].week_id}")
                
                # Afficher les banques distinctes
                banks = set(item.bank_name for item in raw_data)
                print(f"Banques disponibles: {', '.join(banks)}")
                
                # Afficher le contenu de raw_data pour le premier enregistrement
                print("\nContenu de raw_data pour le premier enregistrement:")
                raw_data_content = raw_data[0].raw_data
                print(f"Type: {type(raw_data_content)}")
                print(f"Contenu: {raw_data_content[:200]}...")
                
                # Essayer de parser le JSON
                try:
                    if isinstance(raw_data_content, str):
                        parsed_data = json.loads(raw_data_content)
                        print(f"JSON valide: {parsed_data}")
                    else:
                        print(f"Le contenu n'est pas une chaîne de caractères, mais un {type(raw_data_content)}")
                except Exception as e:
                    print(f"Erreur lors du parsing JSON: {str(e)}")
        except Exception as e:
            print(f"Erreur lors de la vérification de BankDataRaw: {str(e)}")
            
            # Vérifier si la table existe
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bank_data_raw'").fetchall()
            if result:
                print("La table bank_data_raw existe dans la base de données.")
            else:
                print("La table bank_data_raw n'existe PAS dans la base de données.")
    finally:
        db.close()

if __name__ == "__main__":
    main() 