# Documentation - Bibliothèque Numérique en Ligne

Bienvenue dans la documentation complète du projet de bibliothèque numérique développé avec Django.

## 📚 Table des Matières

1. [Introduction](01_INTRODUCTION.md)
2. [Installation](02_INSTALLATION.md)
3. [Modèles de Données](03_MODELES.md)
4. [Interface d'Administration](04_ADMIN.md)
5. [Base de Données](05_BASE_DE_DONNEES.md)
6. [Prochaines Étapes](06_PROCHAINES_ETAPES.md)

## 🚀 Démarrage Rapide

### Installation

```bash
# Installer Django
pip install django

# Naviguer vers le projet
cd mon_projet

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver
```

### Accès à l'Application

- **Interface d'administration** : http://127.0.0.1:8000/admin/
- **Page d'accueil** : http://127.0.0.1:8000/

## 📋 Fonctionnalités Actuelles

### ✅ Implémentées

- Gestion complète des livres (ajout, modification, suppression, recherche)
- Gestion des utilisateurs/lecteurs
- Gestion des emprunts et retours avec règles métier : 7 jours, prolongement +5 jours, attente 1 jour pour réemprunter le même livre, limite 3 emprunts actifs et 5 prolongements/mois.
- Espace de gestion pour les bibliothécaires (`/gestion/...`) avec dashboard, listes et formulaires rapides.
- Interface d'administration Django pour les opérations avancées.
- Interface web publique (Accueil, Catalogue, Détails, Mes emprunts, Profil, demande de prolongement)
- Système d'authentification (Inscription, Connexion, Déconnexion)
- Base de données SQLite
- Documentation complète

### 🔜 À Venir

- Statistiques et rapports
- Calcul des retards et amendes
- Notifications par email
- Système de réservation

## 🏗️ Architecture du Projet

```
mon_projet/
├── docs/                        # Documentation
│   ├── README.md               # Ce fichier
│   ├── 01_INTRODUCTION.md
│   ├── 02_INSTALLATION.md
│   ├── 03_MODELES.md
│   ├── 04_ADMIN.md
│   ├── 05_BASE_DE_DONNEES.md
│   └── 06_PROCHAINES_ETAPES.md
├── library/                     # Application principale
│   ├── models.py               # Modèles (Book, User, Emprunts)
│   ├── admin.py                # Configuration de l'admin
│   ├── views.py                # Vues (à développer)
│   └── migrations/             # Migrations de base de données
├── mon_projet/                  # Configuration du projet
│   ├── settings.py             # Configuration
│   └── urls.py                 # Routes
├── manage.py                    # Script de gestion Django
└── db.sqlite3                   # Base de données
```

## 🗂️ Modèles de Données

### Book (Livre)
- Titre, auteur, date de publication
- Catégorie, ISBN
- Exemplaires totaux, disponibilité dérivée (copies disponibles)

### User (Utilisateur)
- Nom, email
- Date d'inscription

### Emprunts
- Livre emprunté
- Utilisateur emprunteur
- Date d'emprunt, date de retour

## 🔧 Commandes Utiles

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver

# Ouvrir le shell Django
python manage.py shell

# Sauvegarder les données
python manage.py dumpdata > backup.json

# Restaurer les données
python manage.py loaddata backup.json
```

## 📖 Guide de Lecture

### Pour Débuter
1. Lisez [01_INTRODUCTION.md](01_INTRODUCTION.md) pour comprendre le projet
2. Suivez [02_INSTALLATION.md](02_INSTALLATION.md) pour installer l'application
3. Consultez [04_ADMIN.md](04_ADMIN.md) pour utiliser l'interface d'administration
4. Lisez [08_AUTHENTIFICATION.md](08_AUTHENTIFICATION.md) pour l'inscription/connexion

### Pour Développer
1. Étudiez [03_MODELES.md](03_MODELES.md) pour comprendre la structure des données
2. Consultez [05_BASE_DE_DONNEES.md](05_BASE_DE_DONNEES.md) pour la gestion de la base
3. Planifiez avec [06_PROCHAINES_ETAPES.md](06_PROCHAINES_ETAPES.md)

## 🎯 Objectifs du Projet

### Fonctionnalités Indispensables
- ✅ Gestion des livres
- ✅ Gestion des utilisateurs
- ✅ Emprunts et retours
- ✅ Sauvegarde des données
- ✅ Interface de base

### Fonctionnalités d'Agrément
- ⏳ Statistiques et rapports
- ⏳ Gestion avancée des emprunts
- ⏳ Système d'authentification
- ⏳ Interface graphique
- ⏳ Export des données
- ⏳ Système de réservation
- ⏳ Notation et recommandations
- ⏳ Notifications par email

## 🛠️ Technologies

- **Framework** : Django 5.2.7
- **Base de données** : SQLite3
- **Langage** : Python 3.x
- **Interface** : Django Admin

## 📝 Notes Importantes

### Sécurité
- Ne jamais exposer `SECRET_KEY` en production
- Désactiver `DEBUG = False` en production
- Utiliser des variables d'environnement pour les secrets

### Performance
- Utiliser `select_related()` pour les relations ForeignKey
- Créer des index sur les champs fréquemment recherchés
- Limiter les résultats avec pagination

### Bonnes Pratiques
- Écrire des tests pour chaque fonctionnalité
- Utiliser Git pour le contrôle de version
- Documenter le code et les fonctionnalités
- Faire des sauvegardes régulières

## 🤝 Contribution

Ce projet est en développement actif. Les contributions sont les bienvenues !

### Comment Contribuer
1. Créer une branche pour votre fonctionnalité
2. Développer et tester
3. Documenter les changements
4. Soumettre vos modifications

## 📞 Support

Pour toute question ou problème :
- Consultez la documentation dans le dossier `docs/`
- Vérifiez les logs d'erreur Django
- Utilisez `python manage.py check` pour diagnostiquer

## 📅 Historique des Versions

### Version 2.0.0 (Option 3 - Bibliothèque Hybride, novembre 2025)
- ✅ Passage à un fonctionnement "bibliothèque hybride" (physique + numérique)
- ✅ Ajout du modèle `DemandeProlongement` pour gérer les demandes de prolongation d'emprunt (approuver / rejeter côté staff)
- ✅ Mise à jour du modèle `Emprunts` pour fiabiliser les calculs de dates (`days_remaining`, `is_overdue`)
- ✅ Encadrement des actions d'emprunt/retour côté lecteur via des règles métier strictes (limite d'emprunts actifs, délai d'1 jour pour réemprunter le même livre)
- ✅ Ajout d'un bouton "Demander un prolongement" sur le profil lecteur avec règles métier strictes (quota mensuel, pas de retard, fenêtre temporelle précise)
- ✅ Création d'un **dashboard de gestion** dédié aux bibliothécaires (`/gestion/dashboard/`)
  - Statistiques : nombre de livres, exemplaires disponibles, lecteurs inscrits, emprunts actifs
  - Listes : emprunts en retard, emprunts à rendre bientôt, demandes de prolongement en attente
  - Actions rapides : enregistrement d'un nouvel emprunt, enregistrement d'un retour
- ✅ Nouvelle base de template `admin_base.html` pour séparer clairement l'interface staff du site lecteur
- ✅ Intégration avec l'admin Django :
  - Bouton "Aller sur le site" de l'admin qui pointe vers `/gestion/dashboard/`
  - Accès complémentaire aux modèles via l'admin Django classique pour les opérations avancées
- ✅ Mise à jour de la documentation pour refléter ce fonctionnement (ce fichier + cahier des charges Option 3)

### Version 1.0.0 (28 octobre 2025)
- ✅ Configuration initiale du projet Django
- ✅ Création des modèles Book, User, Emprunts
- ✅ Configuration de l'interface d'administration
- ✅ Migrations de base de données
- ✅ Documentation complète

## 🎓 Ressources d'Apprentissage

- [Documentation Django](https://docs.djangoproject.com/)
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)
- [Real Python Django](https://realpython.com/tutorials/django/)

## 📄 Licence

Ce projet est développé à des fins éducatives.

## 👨‍💻 Auteur

Développé avec l'assistance de Cascade AI - Octobre 2025

---

**Bon développement ! 🚀**
