from django.urls import path
from . import views

urlpatterns = [
    path('encadrement/', views.dashboard_encadrement, name='dashboard_encadrement'),
]