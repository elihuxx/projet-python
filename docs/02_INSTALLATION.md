# Guide d'Installation

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (optionnel)

## Étapes d'installation

### 1. Vérifier l'installation de Python

```bash
python --version
```

Vous devriez voir quelque chose comme : `Python 3.x.x`

### 2. Créer un environnement virtuel (recommandé)

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate

# Sur macOS/Linux :
source venv/bin/activate
```

### 3. Installer Django

```bash
pip install django
```

### 4. Vérifier l'installation de Django

```bash
python -m django --version
```

Vous devriez voir : `5.2.7` (ou une version similaire)

### 5. Structure du projet

Le projet est déjà créé avec la structure suivante :
- **mon_projet/** : Répertoire racine
- **mon_projet/mon_projet/** : Configuration du projet
- **mon_projet/library/** : Application principale avec les modèles

### 6. Appliquer les migrations

Les migrations créent les tables dans la base de données :

```bash
cd mon_projet
python manage.py migrate
```

### 7. Créer un superutilisateur

Pour accéder à l'interface d'administration :

```bash
python manage.py createsuperuser
```

Suivez les instructions :
- **Username** : Choisissez un nom d'utilisateur (ex: admin)
- **Email** : Votre adresse email (optionnel)
- **Password** : Choisissez un mot de passe sécurisé

### 8. Démarrer le serveur de développement

```bash
python manage.py runserver
```

Le serveur démarre sur : `http://127.0.0.1:8000/`

### 9. Accéder à l'interface d'administration

Ouvrez votre navigateur et allez à :
```
http://127.0.0.1:8000/admin/
```

Connectez-vous avec les identifiants créés à l'étape 7.

## Dépannage

### Erreur : "No module named django"
```bash
pip install django
```

### Erreur : "Port already in use"
```bash
# Utilisez un autre port
python manage.py runserver 8080
```

### Erreur de migration
```bash
# Recréer les migrations
python manage.py makemigrations
python manage.py migrate
```

## Commandes utiles

```bash
# Créer des migrations après modification des modèles
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver

# Ouvrir le shell Django
python manage.py shell

# Vérifier les migrations
python manage.py showmigrations
```
