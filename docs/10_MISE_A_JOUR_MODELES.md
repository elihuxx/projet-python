# Mise à Jour des Modèles - Support du Workflow Complet

## Vue d'ensemble

Cette mise à jour majeure des modèles implémente toutes les fonctionnalités du workflow de la bibliothèque numérique : exemplaires multiples, prolongements, quotas mensuels, et gestion automatique des dates.

## Modifications des Modèles

### 1. Modèle `Book` (Livre)

#### Champs ajoutés
- **`total_copies`** (IntegerField) : Nombre total d'exemplaires du livre
  - Valeur par défaut : 1
  - Permet de gérer plusieurs exemplaires du même livre

#### Champs supprimés
- **`available`** (BooleanField) : Remplacé par un calcul dynamique

#### Propriétés ajoutées
- **`available_copies`** : Calcule le nombre d'exemplaires disponibles
  - Formule : `total_copies - emprunts_actifs`
- **`is_available`** : Vérifie si au moins un exemplaire est disponible
  - Retourne `True` si `available_copies > 0`

### 2. Modèle `User` (Utilisateur)

#### Champs ajoutés
- **`extensions_this_month`** (IntegerField) : Compteur de prolongements ce mois
  - Valeur par défaut : 0
  - Maximum : 5 par mois
- **`last_reset_date`** (DateField) : Date de dernière réinitialisation du compteur
  - Permet de réinitialiser automatiquement chaque mois

#### Méthodes ajoutées
- **`reset_monthly_extensions()`** : Réinitialise le compteur si nouveau mois
- **`active_borrows_count`** : Compte les emprunts actifs
- **`can_borrow`** : Vérifie si peut emprunter (< 3 emprunts)
- **`remaining_extensions`** : Calcule les prolongements restants (5 - utilisés)

### 3. Modèle `Emprunts` (Emprunt)

#### Champs modifiés
- **`date_emprunt`** : Changé de DateField à DateTimeField
  - Permet un suivi plus précis
- **`date_retour`** : Changé de DateField à DateTimeField

#### Champs ajoutés
- **`date_fin_prevue`** (DateField) : Date de fin prévue de l'emprunt
  - Calculée automatiquement : date_emprunt + 7 jours
  - Peut être prolongée de 5 jours
- **`deja_prolonge`** (BooleanField) : Indique si déjà prolongé
  - Valeur par défaut : False
  - Maximum 1 prolongement par emprunt

#### Propriétés ajoutées
- **`is_active`** : Vérifie si l'emprunt est actif (pas retourné)
- **`days_remaining`** : Calcule les jours restants
- **`is_overdue`** : Vérifie si en retard
- **`can_extend`** : Vérifie si peut être prolongé
  - Conditions : actif, pas déjà prolongé, quota disponible, avant J+7

#### Méthodes ajoutées
- **`extend()`** : Prolonge l'emprunt de 5 jours
  - Vérifie les conditions
  - Met à jour le compteur de l'utilisateur
- **`return_book()`** : Retourne le livre
  - Enregistre la date de retour

## Mise à Jour de l'Interface Admin

### Admin Book (Livres)

#### Affichage
- Nombre total d'exemplaires (éditable)
- Disponibilité avec couleur :
  - 🟢 Vert : Exemplaires disponibles
  - 🔴 Rouge : Tous empruntés

### Admin User (Utilisateurs)

#### Affichage
- Emprunts actifs (X/3) avec couleur
- Prolongements restants (X/5) avec couleur

### Admin Emprunts

#### Affichage
- Statut avec couleur :
  - 🟢 Vert : En cours
  - 🟠 Orange : Bientôt dû (≤ 2 jours)
  - 🔴 Rouge : EN RETARD
  - ⚫ Gris : Retourné
- Jours restants
- Indicateur de prolongement

#### Actions groupées
- **Retourner les livres sélectionnés** : Retourne plusieurs livres en un clic
- **Prolonger les emprunts sélectionnés** : Prolonge si possible

## Migration de Données

### Commande exécutée

```bash
python manage.py makemigrations
python manage.py migrate
```

### Fichier de migration

`library/migrations/0002_alter_book_options_alter_emprunts_options_and_more.py`

### Changements appliqués

1. **Books** : Ajout de `total_copies`, suppression de `available`
2. **Users** : Ajout de `extensions_this_month` et `last_reset_date`
3. **Emprunts** : Ajout de `date_fin_prevue` et `deja_prolonge`
4. Mise à jour des labels (verbose_name) en français
5. Ajout des Meta options (ordering, verbose_name_plural)

## Exemples d'Utilisation

### Vérifier la disponibilité d'un livre

```python
from library.models import Book

book = Book.objects.get(isbn='9780451524935')
print(f"Exemplaires disponibles : {book.available_copies}/{book.total_copies}")
print(f"Disponible : {book.is_available}")
```

### Vérifier les quotas d'un utilisateur

```python
from library.models import User

user = User.objects.get(email='user@example.com')
print(f"Emprunts actifs : {user.active_borrows_count}/3")
print(f"Peut emprunter : {user.can_borrow}")
print(f"Prolongements restants : {user.remaining_extensions}/5")
```

### Gérer un emprunt

```python
from library.models import Emprunts

# Récupérer un emprunt
emprunt = Emprunts.objects.get(id=1)

# Vérifier le statut
print(f"Actif : {emprunt.is_active}")
print(f"Jours restants : {emprunt.days_remaining}")
print(f"En retard : {emprunt.is_overdue}")
print(f"Peut prolonger : {emprunt.can_extend}")

# Prolonger
if emprunt.can_extend:
    emprunt.extend()
    print("Prolongé de 5 jours !")

# Retourner
if emprunt.is_active:
    emprunt.return_book()
    print("Livre retourné !")
```

### Créer un emprunt

```python
from library.models import Book, User, Emprunts

book = Book.objects.get(isbn='9780451524935')
user = User.objects.get(email='user@example.com')

# Vérifications
if not book.is_available:
    print("Aucun exemplaire disponible")
elif not user.can_borrow:
    print("Limite de 3 emprunts atteinte")
else:
    # Créer l'emprunt (date_fin_prevue calculée automatiquement)
    emprunt = Emprunts.objects.create(
        book=book,
        user=user
    )
    print(f"Emprunt créé ! À retourner le {emprunt.date_fin_prevue}")
```

## Règles Métier Implémentées

### ✅ Emprunt
- Durée : 7 jours (calculée automatiquement)
- Maximum 3 emprunts simultanés par utilisateur
- Vérification de disponibilité des exemplaires

### ✅ Prolongement
- Durée : +5 jours
- Maximum 1 prolongement par emprunt
- Maximum 5 prolongements par mois par utilisateur
- Possible jusqu'à J+6

### ✅ Retour
- Enregistrement de la date de retour
- Libération automatique de l'exemplaire

### ⏳ À implémenter
- Délai de 1 jour avant réemprunt du même livre
- Retour automatique à J+7 à 23h59
- Notifications par email

## Tests dans l'Admin

### 1. Tester les exemplaires multiples

1. Aller dans Books
2. Modifier un livre : `total_copies = 3`
3. Créer 3 emprunts pour ce livre
4. Vérifier que la disponibilité affiche `0/3 (tous empruntés)`

### 2. Tester les prolongements

1. Créer un emprunt récent (< 7 jours)
2. Dans Emprunts, sélectionner l'emprunt
3. Action : "Prolonger les emprunts sélectionnés"
4. Vérifier que `date_fin_prevue` a été augmentée de 5 jours
5. Vérifier que `deja_prolonge = True`

### 3. Tester le quota mensuel

1. Créer 5 emprunts pour un utilisateur
2. Prolonger les 5 emprunts
3. Créer un 6ème emprunt
4. Essayer de le prolonger → Devrait échouer

### 4. Tester le retour

1. Sélectionner des emprunts actifs
2. Action : "Retourner les livres sélectionnés"
3. Vérifier que `date_retour` est renseignée
4. Vérifier que la disponibilité du livre a augmenté

## Commandes Utiles

### Réinitialiser les compteurs mensuels

```bash
python manage.py shell
```

```python
from library.models import User
for user in User.objects.all():
    user.extensions_this_month = 0
    user.save()
```

### Voir les emprunts actifs

```bash
python manage.py shell -c "from library.models import Emprunts; print(Emprunts.objects.filter(date_retour__isnull=True).count())"
```

### Voir les livres disponibles

```bash
python manage.py shell -c "from library.models import Book; [print(f'{b.title}: {b.available_copies}/{b.total_copies}') for b in Book.objects.all()[:10]]"
```

## Prochaines Étapes

1. **Interface utilisateur** - Créer les pages pour emprunter/retourner/prolonger
2. **Délai de réemprunt** - Implémenter le délai de 1 jour
3. **Retour automatique** - Tâche cron pour retourner à J+7
4. **Notifications** - Emails de rappel et confirmation
5. **Historique** - Page d'historique des emprunts

---

**Date de création** : Octobre 2025  
**Dernière mise à jour** : Octobre 2025  
**Version** : 2.0
