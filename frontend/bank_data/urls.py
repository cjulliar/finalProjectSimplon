from django.urls import path
from . import views

app_name = 'bank_data'

urlpatterns = [
    path('', views.bank_data_list, name='list'),
    path('<int:bank_data_id>/', views.bank_data_detail, name='detail'),
] 