from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('connexion/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('apres-connexion/', views.apres_connexion, name='apres_connexion'),
]