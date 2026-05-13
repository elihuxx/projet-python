# Documentation - Bibliothèque Numérique en Ligne

## Vue d'ensemble du projet

Cette application est une **bibliothèque hybride (physique + numérique)** développée avec Django. Elle permet de gérer des livres, des utilisateurs (lecteurs) et des emprunts selon les règles décrites dans le cahier des charges *Option 3* :

- Les **lecteurs** consultent le catalogue en ligne, suivent leurs emprunts et peuvent **demander un prolongement**.
- Les **bibliothécaires (staff)** enregistrent les emprunts et retours et traitent les demandes via un **dashboard dédié** et l’admin Django.

## Objectifs du projet

### Fonctionnalités Indispensables (version actuelle)
- **Gestion des livres** : Ajouter, supprimer, modifier, rechercher et afficher les livres (via admin + dashboard staff)
- **Gestion des utilisateurs/lecteurs** : Créés et gérés par l’admin Django
- **Emprunts et retours** : Enregistrés par les bibliothécaires, avec quotas et durées (7 jours + prolongement 5 jours)
- **Demandes de prolongement** : Envoyées par les lecteurs, approuvées/rejetées par le staff
- **Sauvegarde des données** : Utilisation de SQLite pour la persistance des données
- **Interface d'administration + dashboard staff** : Gestion complète de la bibliothèque

### Fonctionnalités d'Agrément (Futures)
- Statistiques et rapports
- Gestion avancée des emprunts (retards, amendes)
- Système d'authentification avancé
- Notifications par email
- Système de réservation
- Notation et recommandations

## Technologies utilisées

- **Framework** : Django 5.2.7
- **Base de données** : SQLite3
- **Langage** : Python 3.x
- **Interface** : Django Admin

## Structure du projet

```
mon_projet/
├── manage.py                    # Script de gestion Django
├── db.sqlite3                   # Base de données SQLite
├── docs/                        # Documentation du projet
├── mon_projet/                  # Configuration du projet
│   ├── settings.py             # Configuration globale
│   ├── urls.py                 # Routes principales
│   ├── wsgi.py                 # Configuration WSGI
│   └── asgi.py                 # Configuration ASGI
└── library/                     # Application principale
    ├── models.py               # Modèles de données
    ├── admin.py                # Configuration de l'admin
    ├── views.py                # Vues (à venir)
    ├── urls.py                 # Routes de l'application (à venir)
    └── migrations/             # Migrations de base de données
```

## Auteur

Projet développé avec l'assistance de Cascade AI.

## Date de création

28 octobre 2025
