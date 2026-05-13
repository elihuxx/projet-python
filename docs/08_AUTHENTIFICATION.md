# Système d'Authentification

## Vue d'ensemble

Le système d'authentification permet aux utilisateurs de :
- **S'inscrire** avec un compte personnel
- **Se connecter** pour accéder aux fonctionnalités
- **Se déconnecter** en toute sécurité

## Architecture

### Modèles utilisés

Le système utilise deux types d'utilisateurs :

1. **Django User** (`django.contrib.auth.models.User`)
   - Gère l'authentification (username, password)
   - Utilisé pour la connexion/déconnexion
   - Intégré au système de permissions Django

2. **Library User** (`library.models.User`)
   - Stocke les informations spécifiques à la bibliothèque
   - Lié aux emprunts de livres
   - Contient : name, email, membership_date

### Relation entre les deux modèles

Lors de l'inscription, les deux utilisateurs sont créés simultanément :
- Un utilisateur Django pour l'authentification
- Un utilisateur Library pour les emprunts

## Fichiers créés

### 1. URLs (`library/urls.py`)

```python
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
]
```

### 2. Formulaires (`library/forms.py`)

#### RegisterForm
- Hérite de `UserCreationForm`
- Champs : name, email, password1, password2
- Utilise l'email comme identifiant (username=email)
- Validation automatique des mots de passe
- Style Bootstrap intégré

#### LoginForm
- Champs : email, password
- Validation simple
- Style Bootstrap intégré

### 3. Vues (`library/views.py`)

#### `register(request)`
- Affiche le formulaire d'inscription
- Crée un utilisateur Django et Library
- Connecte automatiquement après inscription
- Redirige vers la page d'accueil

#### `login_view(request)`
- Affiche le formulaire de connexion
- Authentifie l'utilisateur
- Gère les redirections (paramètre `next`)
- Affiche des messages d'erreur si échec

#### `logout_view(request)`
- Déconnecte l'utilisateur
- Affiche un message de confirmation
- Redirige vers la page d'accueil

#### `home(request)`
- Page d'accueil
- Affichage différent selon l'état de connexion

#### `profile(request)`
- Page de profil utilisateur (protégée)
- Affiche les informations du lecteur, ses emprunts actifs et l'historique

### 4. Templates

#### `base.html`
- Template de base avec navigation
- Barre de navigation responsive
- Affichage conditionnel des liens (connecté/déconnecté)
- Système de messages flash
- Design moderne avec Bootstrap 5

#### `home.html`
- Page d'accueil
- Vue différente pour utilisateurs connectés/non connectés
- Cartes de présentation des fonctionnalités

#### `register.html`
- Formulaire d'inscription
- Validation côté client et serveur
- Messages d'erreur clairs
- Lien vers la page de connexion

#### `login.html`
- Formulaire de connexion
- Option "Se souvenir de moi"
- Lien vers inscription et récupération de mot de passe
- Messages d'erreur

## Configuration (`settings.py`)

```python
# Langue et fuseau horaire
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'

# Redirections d'authentification
LOGIN_URL = 'library:login'
LOGIN_REDIRECT_URL = 'library:home'
LOGOUT_REDIRECT_URL = 'library:home'
```

## Fonctionnalités

### 1. Inscription

**URL** : `/register/`

**Processus** :
1. L'utilisateur remplit le formulaire
2. Validation des données (email unique, mot de passe fort)
3. Création de l'utilisateur Django
4. Création de l'utilisateur Library
5. Connexion automatique
6. Redirection vers l'accueil

**Validations** :
- Username unique
- Email valide et unique
- Mot de passe minimum 8 caractères
- Confirmation du mot de passe

### 2. Connexion

**URL** : `/login/`

**Processus** :
1. L'utilisateur entre ses identifiants
2. Authentification via Django
3. Création d'une session
4. Redirection vers la page demandée ou l'accueil

**Sécurité** :
- Mot de passe hashé (PBKDF2)
- Protection CSRF
- Session sécurisée

### 3. Déconnexion

**URL** : `/logout/`

**Processus** :
1. Destruction de la session
2. Message de confirmation
3. Redirection vers l'accueil

## Sécurité

### Mesures implémentées

1. **Hachage des mots de passe**
   - Utilisation de PBKDF2 par défaut
   - Salt automatique
   - Impossible de récupérer le mot de passe en clair

2. **Protection CSRF**
   - Token CSRF sur tous les formulaires
   - Validation automatique par Django

3. **Validation des données**
   - Validation côté serveur
   - Messages d'erreur clairs
   - Prévention des injections SQL

4. **Sessions sécurisées**
   - Cookie httponly
   - Expiration automatique
   - Régénération après connexion

### Bonnes pratiques

- Ne jamais stocker les mots de passe en clair
- Utiliser HTTPS en production
- Limiter les tentatives de connexion (à implémenter)
- Activer l'authentification à deux facteurs (optionnel)

## Design et UX

### Technologies utilisées

- **Bootstrap 5** : Framework CSS moderne
- **Font Awesome 6** : Icônes
- **Gradient backgrounds** : Design attractif
- **Responsive design** : Compatible mobile

### Caractéristiques

- Interface intuitive
- Messages flash colorés
- Formulaires clairs avec aide contextuelle
- Navigation fluide
- Design cohérent

## Tests manuels

### Test d'inscription

1. Aller sur `/register/`
2. Remplir tous les champs
3. Vérifier la création du compte
4. Vérifier la connexion automatique
5. Vérifier la création dans l'admin Django

### Test de connexion

1. Se déconnecter
2. Aller sur `/login/`
3. Entrer des identifiants valides
4. Vérifier la connexion
5. Vérifier l'affichage du nom d'utilisateur

### Test de déconnexion

1. Être connecté
2. Cliquer sur "Déconnexion"
3. Vérifier la déconnexion
4. Vérifier le message de confirmation

### Test de validation

1. Essayer de s'inscrire avec un email invalide
2. Essayer un mot de passe trop court
3. Essayer un username déjà pris
4. Vérifier les messages d'erreur

## Commandes utiles

### Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### Lancer le serveur

```bash
python manage.py runserver
```

### Accéder aux pages

- Accueil : http://127.0.0.1:8000/
- Inscription : http://127.0.0.1:8000/register/
- Connexion : http://127.0.0.1:8000/login/
- Profil : http://127.0.0.1:8000/profile/
- Admin : http://127.0.0.1:8000/admin/

## Prochaines améliorations

### Court terme

- [x] Page de profil utilisateur
- [ ] Modification des informations personnelles
- [ ] Changement de mot de passe
- [ ] Récupération de mot de passe par email

### Moyen terme

- [ ] Authentification par email
- [ ] Authentification sociale (Google, Facebook)
- [ ] Limitation des tentatives de connexion
- [ ] Historique de connexion

### Long terme

- [ ] Authentification à deux facteurs (2FA)
- [ ] Biométrie (si applicable)
- [ ] Single Sign-On (SSO)
- [ ] OAuth2 provider

## Dépannage

### Erreur "CSRF token missing"

**Solution** : Vérifier que `{% csrf_token %}` est présent dans le formulaire

### Erreur "User already exists"

**Solution** : Choisir un autre username ou email

### Page blanche après connexion

**Solution** : Vérifier les URLs et les redirections dans `settings.py`

### Formulaire ne s'affiche pas

**Solution** : Vérifier que l'app `library` est dans `INSTALLED_APPS`

## Ressources

- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/)
- [Django Forms](https://docs.djangoproject.com/en/5.2/topics/forms/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Font Awesome Icons](https://fontawesome.com/icons)

---

**Date de création** : Octobre 2025  
**Dernière mise à jour** : Octobre 2025  
**Version** : 1.0
