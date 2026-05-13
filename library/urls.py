from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Pages d'authentification
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Page d'accueil
    path('', views.home, name='home'),
    
    # Catalogue
    path('catalog/', views.catalog, name='catalog'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    
    # Emprunts
    path('my-borrows/', views.my_borrows, name='my_borrows'),
    
    # Profil utilisateur
    path('profile/', views.profile, name='profile'),
    path('demander-prolongement/<int:emprunt_id>/', views.demander_prolongement, name='demander_prolongement'),
    
    # Conditions d'utilisation
    path('terms/', views.terms, name='terms'),

    # Dashboard admin personnalisé (gestion de la bibliothèque)
    path('gestion/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('gestion/livres/', views.admin_livres, name='admin_livres'),
    path('gestion/emprunts/', views.admin_emprunts, name='admin_emprunts'),
    path('gestion/utilisateurs/', views.admin_utilisateurs, name='admin_utilisateurs'),
    path('gestion/emprunter/', views.admin_enregistrer_emprunt, name='admin_enregistrer_emprunt'),
    path('gestion/retourner/<int:emprunt_id>/', views.admin_enregistrer_retour, name='admin_enregistrer_retour'),
]
