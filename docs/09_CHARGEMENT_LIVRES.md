# Chargement des Livres dans la Base de Données

## Vue d'ensemble

Cette étape permet de charger automatiquement une liste de livres prédéfinis dans la base de données via une commande Django personnalisée.

## Fichiers créés

### 1. Structure des dossiers

```
library/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── load_books.py
```

### 2. Commande personnalisée (`load_books.py`)

Une commande Django qui :
- Lit une liste de livres prédéfinis
- Crée ou met à jour chaque livre dans la base de données
- Utilise `update_or_create()` pour éviter les doublons (basé sur l'ISBN)
- Affiche un rapport de l'opération

## Liste des livres chargés

### Livres internationaux

1. **1984** - George Orwell (1949)
   - Catégorie : Roman dystopique
   - ISBN : 9780451524935

2. **To Kill a Mockingbird** - Harper Lee (1960)
   - Catégorie : Roman classique
   - ISBN : 9780061120084

3. **The Catcher in the Rye** - J.D. Salinger (1951)
   - Catégorie : Roman initiatique
   - ISBN : 9780316769488

4. **Pride and Prejudice** - Jane Austen (1813)
   - Catégorie : Romance
   - ISBN : 9781503290563

5. **The Great Gatsby** - F. Scott Fitzgerald (1925)
   - Catégorie : Roman moderne
   - ISBN : 9780743273565

6. **Harry Potter and the Philosopher's Stone** - J.K. Rowling (1997)
   - Catégorie : Fantasy
   - ISBN : 9780747532699

7. **The Alchemist** - Paulo Coelho (1988)
   - Catégorie : Philosophie / Fiction
   - ISBN : 9780061122415

### Littérature africaine

8. **Allah n'est pas obligé** - Ahmadou Kourouma (2000)
   - Catégorie : Roman africain
   - ISBN : 9782070416808

9. **Les Soleils des indépendances** - Ahmadou Kourouma (1970)
   - Catégorie : Roman politique
   - ISBN : 9782070377000

10. **Le vieux nègre et la médaille** - Ferdinand Oyono (1956)
    - Catégorie : Roman colonial
    - ISBN : 9782070363126

11. **Une si longue lettre** - Mariama Bâ (1979)
    - Catégorie : Roman épistolaire
    - ISBN : 9782266023167

12. **Le devoir de violence** - Yambo Ouologuem (1968)
    - Catégorie : Roman historique
    - ISBN : 9782070378236

13. **Blé de misère** - Bernard Dadié (1956)
    - Catégorie : Nouvelles africaines
    - ISBN : 9782708702362

14. **Climbié** - Bernard Dadié (1956)
    - Catégorie : Roman autobiographique
    - ISBN : 9782708702355

## Utilisation

### Charger les livres

```bash
python manage.py load_books
```

### Résultat attendu

```
[OK] Cree: 1984
[OK] Cree: To Kill a Mockingbird
[OK] Cree: The Catcher in the Rye
...
Termine! 14 livre(s) cree(s), 0 livre(s) mis a jour.
```

### Vérifier les livres dans la base

```bash
python manage.py shell
```

```python
from library.models import Book

# Compter les livres
print(Book.objects.count())

# Afficher tous les livres
for book in Book.objects.all():
    print(f"{book.title} - {book.author}")

# Filtrer par catégorie
romans_africains = Book.objects.filter(category__icontains='africain')
for book in romans_africains:
    print(book.title)
```

## Fonctionnalités de la commande

### 1. Création ou mise à jour

La commande utilise `update_or_create()` qui :
- Crée le livre s'il n'existe pas (basé sur l'ISBN)
- Met à jour le livre s'il existe déjà
- Évite les doublons

### 2. Rapport détaillé

- `[OK] Cree:` - Nouveau livre créé
- `[MAJ] Mis a jour:` - Livre existant mis à jour
- Compteur final des opérations

### 3. Tous les livres disponibles

Par défaut, tous les livres sont marqués comme `available=True`

## Code de la commande

```python
from django.core.management.base import BaseCommand
from library.models import Book

class Command(BaseCommand):
    help = 'Charge les livres initiaux dans la base de données'

    def handle(self, *args, **kwargs):
        books_data = [
            {
                'title': '1984',
                'author': 'George Orwell',
                'published_date': '1949-06-08',
                'category': 'Roman dystopique',
                'isbn': '9780451524935',
            },
            # ... autres livres
        ]

        for book_data in books_data:
            book, created = Book.objects.update_or_create(
                isbn=book_data['isbn'],
                defaults={
                    'title': book_data['title'],
                    'author': book_data['author'],
                    'published_date': book_data['published_date'],
                    'category': book_data['category'],
                    'available': True,
                }
            )
```

## Ajouter de nouveaux livres

Pour ajouter de nouveaux livres, modifiez le fichier `load_books.py` :

```python
books_data = [
    # Livres existants...
    {
        'title': 'Nouveau Livre',
        'author': 'Auteur',
        'published_date': '2025-01-01',
        'category': 'Catégorie',
        'isbn': '9781234567890',
    },
]
```

Puis relancez la commande :

```bash
python manage.py load_books
```

## Réinitialiser les livres

Si vous voulez supprimer tous les livres et recommencer :

```bash
python manage.py shell
```

```python
from library.models import Book
Book.objects.all().delete()
exit()
```

Puis rechargez :

```bash
python manage.py load_books
```

## Vérification dans l'admin

1. Connectez-vous à l'admin : http://127.0.0.1:8000/admin/
2. Allez dans "Books"
3. Vous devriez voir tous les livres chargés

## Avantages de cette approche

### 1. Reproductible
- Même commande sur tous les environnements
- Facile à exécuter après une nouvelle installation

### 2. Idempotent
- Peut être exécuté plusieurs fois sans créer de doublons
- Met à jour les livres existants

### 3. Versionnable
- Le code est dans Git
- Facile de suivre les changements

### 4. Extensible
- Facile d'ajouter de nouveaux livres
- Peut être modifié pour lire depuis un fichier CSV/JSON

## Prochaines améliorations possibles

### Court terme
- [ ] Lire les livres depuis un fichier CSV
- [ ] Ajouter une option pour supprimer les livres avant de charger
- [ ] Ajouter plus de validations

### Moyen terme
- [ ] Import depuis une API externe
- [ ] Gestion des images de couverture
- [ ] Import en masse avec barre de progression

### Long terme
- [ ] Interface admin pour importer des livres
- [ ] Synchronisation avec des bibliothèques en ligne
- [ ] Détection automatique des métadonnées via ISBN

## Commandes utiles

### Compter les livres par catégorie

```python
from library.models import Book
from django.db.models import Count

Book.objects.values('category').annotate(count=Count('id'))
```

### Trouver les livres disponibles

```python
Book.objects.filter(available=True).count()
```

### Livres par auteur

```python
Book.objects.filter(author__icontains='Kourouma')
```

## Dépannage

### Erreur "No such table: library_book"

**Solution** : Exécutez les migrations d'abord

```bash
python manage.py migrate
```

### Erreur "Duplicate entry for key 'isbn'"

**Solution** : L'ISBN existe déjà. La commande devrait mettre à jour automatiquement.

### Caractères spéciaux mal affichés

**Solution** : Problème d'encodage Windows. Les livres sont correctement stockés dans la base de données.

---

**Date de création** : Octobre 2025  
**Dernière mise à jour** : Octobre 2025  
**Version** : 1.0
