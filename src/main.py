import pandas as pd
from pathlib import Path
from db.database import engine, Base

def init_db():
    """Initialise la base de données"""
    Base.metadata.create_all(bind=engine)

def read_excel_data():
    """Lit les données du fichier Excel"""
    excel_path = Path("docs/DonneeBanque.xlsx")
    if excel_path.exists():
        df = pd.read_excel(excel_path)
        print("Données Excel chargées avec succès :")
        print(f"Nombre de lignes : {len(df)}")
        print(f"Colonnes : {', '.join(df.columns)}")
        return df
    else:
        print(f"Fichier non trouvé : {excel_path}")
        return None

def main():
    print("Initialisation du projet de rapports bancaires...")
    
    # Initialisation de la base de données
    init_db()
    print("Base de données initialisée")
    
    # Test de lecture des données
    data = read_excel_data()
    if data is not None:
        print("\nTest de lecture réussi !")

if __name__ == "__main__":
    main() 