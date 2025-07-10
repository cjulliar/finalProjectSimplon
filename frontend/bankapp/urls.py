from django.urls import path
from . import views

urlpatterns = [
    path('', views.celery_dashboard, name='celery_dashboard'),
] 