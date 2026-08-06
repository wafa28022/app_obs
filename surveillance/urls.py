from django.urls import path
from . import views

urlpatterns = [
    path('region/', views.formulaire_region, name='formulaire_region'),
    path('central/', views.formulaire_central, name='formulaire_central'),
]