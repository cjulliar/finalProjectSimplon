import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class APIClient:
    """
    Client pour interagir avec l'API FastAPI du backend.
    """
    def __init__(self, access_token=None):
        self.base_url = settings.API_URL
        self.access_token = access_token
        self.headers = {
            'Content-Type': 'application/json',
        }
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
            
    def _check_token_validity(self, response):
        """
        Vérifie si le token est valide et le gère en cas d'erreur 401.
        Appelé automatiquement lorsqu'une réponse 401 est reçue.
        
        Note: dans une implémentation complète, on utiliserait un token de rafraîchissement
        pour obtenir un nouveau token sans demander à l'utilisateur de se reconnecter.
        """
        if response.status_code == 401:
            logger.warning(f"Token invalide ou expiré: {self.base_url}")
            # Ici, nous pourrions implémenter un mécanisme de rafraîchissement du token
            # Pour l'instant, nous nous contentons de loguer l'erreur
            
    def _make_request(self, method, endpoint, **kwargs):
        """
        Méthode générique pour effectuer des requêtes avec gestion d'erreur.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = getattr(requests, method.lower())(url, headers=self.headers, **kwargs)
            
            # Vérifier si le token est invalide
            if response.status_code == 401:
                self._check_token_validity(response)
                
            # Lever une exception en cas d'erreur
            response.raise_for_status()
            
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête {method} {url}: {str(e)}")
            raise
    
    def get_bank_data(self, skip=0, limit=100, agence=None, date_debut=None, date_fin=None):
        """Récupérer les données bancaires avec filtres optionnels."""
        params = {'skip': skip, 'limit': limit}
        if agence:
            params['agence'] = agence
        if date_debut:
            params['date_debut'] = date_debut.isoformat()
        if date_fin:
            params['date_fin'] = date_fin.isoformat()
            
        try:
            response = self._make_request('get', '/api/bank-data', params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données bancaires: {str(e)}")
            return []
    
    def get_bank_data_by_id(self, bank_data_id):
        """Récupérer une entrée spécifique de données bancaires par ID."""
        response = requests.get(
            f"{self.base_url}/api/bank-data/{bank_data_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats_by_agency(self):
        """Récupérer les statistiques par agence."""
        try:
            response = self._make_request('get', '/api/bank-data/stats/by-agence')
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques par agence: {str(e)}")
            return []
    
    def get_stats_by_date(self, days=30):
        """Récupérer les statistiques par date."""
        try:
            response = self._make_request('get', '/api/bank-data/stats/by-date', params={'days': days})
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques par date: {str(e)}")
            return []
    
    def create_analysis(self, analysis_request):
        """Créer une nouvelle analyse IA."""
        try:
            response = self._make_request('post', '/api/analyze', json=analysis_request)
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la création d'analyse: {str(e)}")
            raise
    
    def get_analysis(self, analysis_id):
        """Récupérer une analyse IA spécifique par ID."""
        try:
            response = self._make_request('get', f'/api/analyses/{analysis_id}')
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'analyse {analysis_id}: {str(e)}")
            raise
    
    def get_latest_analyses(self, limit=5):
        """Récupérer les dernières analyses IA."""
        try:
            response = self._make_request('get', '/api/analyses', params={'limit': limit})
            return response.json().get('analyses', [])
        except Exception:
            # Si l'API IA n'est pas disponible, renvoyer une liste vide
            return []
    
    def get_visualization(self, visualization_id):
        """Récupérer une visualisation spécifique."""
        try:
            response = self._make_request('get', f'/api/visualizations/{visualization_id}')
            return response.content
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la visualisation {visualization_id}: {str(e)}")
            raise


def get_api_client(request):
    """Créer un client API avec le token de l'utilisateur actuel."""
    # Ici, nous utilisons une approche simplifiée.
    # Dans une implémentation complète, il faudrait gérer le rafraîchissement des tokens.
    token = request.session.get('api_token')
    return APIClient(access_token=token) 