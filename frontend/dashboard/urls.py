from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dernier-rapport/', views.dernier_rapport_view, name='dernier_rapport'),
    path('historique-rapports/', views.historique_rapports_view, name='historique_rapports'),
    path('statistiques/', views.statistiques_view, name='statistiques'),
] 