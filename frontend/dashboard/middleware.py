from .views import get_user_agence

class AgenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ajouter l'agence_name au request
        if request.user.is_authenticated:
            request.agence_name = get_user_agence(request.user.username)
        else:
            request.agence_name = None
        
        response = self.get_response(request)
        return response 