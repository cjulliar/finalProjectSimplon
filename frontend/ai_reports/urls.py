from django.urls import path
from . import views

app_name = 'ai_reports'

urlpatterns = [
    path('', views.report_list, name='list'),
    path('create/', views.report_create, name='create'),
    path('<str:report_id>/', views.report_detail, name='detail'),
    path('email-reports/', views.email_reports, name='email_reports'),
    path('bank-charts/', views.bank_charts, name='bank_charts'),
] 