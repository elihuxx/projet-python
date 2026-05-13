# Documentation de la Base de Données

## Configuration

### Type de Base de Données
- **Système** : SQLite3
- **Fichier** : `db.sqlite3` (à la racine du projet)
- **Avantages** : 
  - Aucune installation requise
  - Fichier unique portable
  - Parfait pour le développement et les petites applications

### Configuration dans `settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## Structure des Tables

### Table : `library_book`

Stocke les informations sur les livres.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Identifiant unique |
| `title` | VARCHAR(200) | NOT NULL | Titre du livre |
| `author` | VARCHAR(100) | NOT NULL | Nom de l'auteur |
| `published_date` | DATE | NOT NULL | Date de publication |
| `category` | VARCHAR(100) | NOT NULL | Catégorie/Genre |
| `isbn` | VARCHAR(13) | UNIQUE, NOT NULL | Numéro ISBN |
| `available` | BOOLEAN | DEFAULT TRUE | Disponibilité |

**Index** : 
- Index unique sur `isbn`

---

### Table : `library_user`

Stocke les informations sur les utilisateurs/lecteurs.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Identifiant unique |
| `name` | VARCHAR(100) | NOT NULL | Nom complet |
| `email` | VARCHAR(254) | UNIQUE, NOT NULL | Adresse email |
| `membership_date` | DATE | NOT NULL | Date d'inscription |

**Index** : 
- Index unique sur `email`

---

### Table : `library_emprunts`

Stocke les transactions d'emprunt.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Identifiant unique |
| `book_id` | INTEGER | FOREIGN KEY, NOT NULL | Référence vers `library_book.id` |
| `user_id` | INTEGER | FOREIGN KEY, NOT NULL | Référence vers `library_user.id` |
| `date_emprunt` | DATE | NOT NULL | Date de l'emprunt |
| `date_retour` | DATE | NULL | Date de retour (NULL si en cours) |

**Clés étrangères** :
- `book_id` → `library_book.id` (ON DELETE CASCADE)
- `user_id` → `library_user.id` (ON DELETE CASCADE)

**Index** :
- Index sur `book_id`
- Index sur `user_id`
- Index sur `date_emprunt`

---

## Relations entre les Tables

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  library_user   │         │ library_emprunts │         │  library_book   │
├─────────────────┤         ├──────────────────┤         ├─────────────────┤
│ id (PK)         │◄────────│ user_id (FK)     │         │ id (PK)         │
│ name            │         │ book_id (FK)     │────────►│ title           │
│ email           │         │ date_emprunt     │         │ author          │
│ membership_date │         │ date_retour      │         │ published_date  │
└─────────────────┘         └──────────────────┘         │ category        │
                                                          │ isbn            │
                                                          │ available       │
                                                          └─────────────────┘
```

---

## Migrations

### Historique des Migrations

#### Migration initiale : `0001_initial.py`

Cette migration crée les trois tables principales :

```python
# library/migrations/0001_initial.py

operations = [
    migrations.CreateModel(
        name='Book',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('title', models.CharField(max_length=200)),
            ('author', models.CharField(max_length=100)),
            ('published_date', models.DateField()),
            ('category', models.CharField(max_length=100)),
            ('isbn', models.CharField(max_length=13, unique=True)),
            ('available', models.BooleanField(default=True)),
        ],
    ),
    migrations.CreateModel(
        name='User',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('name', models.CharField(max_length=100)),
            ('email', models.EmailField(max_length=254, unique=True)),
            ('membership_date', models.DateField(auto_now_add=True)),
        ],
    ),
    migrations.CreateModel(
        name='Emprunts',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('date_emprunt', models.DateField(auto_now_add=True)),
            ('date_retour', models.DateField(blank=True, null=True)),
            ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.book')),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.user')),
        ],
    ),
]
```

### Commandes de Migration

```bash
# Créer de nouvelles migrations après modification des modèles
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations

# Voir le SQL généré par une migration
python manage.py sqlmigrate library 0001

# Annuler une migration (revenir en arrière)
python manage.py migrate library 0000  # Annule toutes les migrations
```

---

## Requêtes SQL Équivalentes

### Exemples de requêtes Django ORM et leur équivalent SQL

#### Créer un livre

**Django ORM** :
```python
Book.objects.create(
    title="Le Petit Prince",
    author="Antoine de Saint-Exupéry",
    published_date="1943-04-06",
    category="Fiction",
    isbn="9782070612758",
    available=True
)
```

**SQL** :
```sql
INSERT INTO library_book (title, author, published_date, category, isbn, available)
VALUES ('Le Petit Prince', 'Antoine de Saint-Exupéry', '1943-04-06', 'Fiction', '9782070612758', 1);
```

#### Rechercher un livre

**Django ORM** :
```python
Book.objects.filter(available=True)
```

**SQL** :
```sql
SELECT * FROM library_book WHERE available = 1;
```

#### Lister les emprunts en cours

**Django ORM** :
```python
Emprunts.objects.filter(date_retour__isnull=True)
```

**SQL** :
```sql
SELECT * FROM library_emprunts WHERE date_retour IS NULL;
```

#### Joindre les tables pour voir les emprunts avec détails

**Django ORM** :
```python
Emprunts.objects.select_related('book', 'user').all()
```

**SQL** :
```sql
SELECT 
    e.*,
    b.title, b.author,
    u.name, u.email
FROM library_emprunts e
INNER JOIN library_book b ON e.book_id = b.id
INNER JOIN library_user u ON e.user_id = u.id;
```

---

## Sauvegarde et Restauration

### Sauvegarder la Base de Données

#### Méthode 1 : Copier le fichier SQLite

```bash
# Sauvegarder
copy db.sqlite3 backup_db.sqlite3

# Restaurer
copy backup_db.sqlite3 db.sqlite3
```

#### Méthode 2 : Utiliser dumpdata (format JSON)

```bash
# Sauvegarder toutes les données
python manage.py dumpdata > backup.json

# Sauvegarder seulement l'application library
python manage.py dumpdata library > library_backup.json

# Restaurer
python manage.py loaddata backup.json
```

### Exporter des Données Spécifiques

```bash
# Exporter seulement les livres
python manage.py dumpdata library.Book > books.json

# Exporter seulement les utilisateurs
python manage.py dumpdata library.User > users.json

# Exporter seulement les emprunts
python manage.py dumpdata library.Emprunts > emprunts.json
```

---

## Accès Direct à la Base de Données

### Utiliser le Shell Django

```bash
python manage.py shell
```

```python
# Dans le shell
from library.models import Book, User, Emprunts

# Compter les livres
Book.objects.count()

# Lister tous les livres disponibles
Book.objects.filter(available=True)

# Voir les emprunts en cours
Emprunts.objects.filter(date_retour__isnull=True)
```

### Utiliser SQLite directement

```bash
# Ouvrir la base de données
sqlite3 db.sqlite3

# Commandes SQLite utiles
.tables                    # Lister toutes les tables
.schema library_book       # Voir la structure d'une table
SELECT * FROM library_book;  # Requête SQL
.quit                      # Quitter
```

---

## Optimisation et Performance

### Index Existants

Django crée automatiquement des index sur :
- Les clés primaires (`id`)
- Les champs uniques (`isbn`, `email`)
- Les clés étrangères (`book_id`, `user_id`)

### Conseils de Performance

1. **Utiliser `select_related()`** pour les relations ForeignKey
2. **Utiliser `prefetch_related()`** pour les relations Many-to-Many
3. **Créer des index** sur les champs fréquemment recherchés
4. **Limiter les résultats** avec `.filter()` plutôt que `.all()`

---

## Maintenance

### Vérifier l'Intégrité de la Base de Données

```bash
# Vérifier les migrations
python manage.py showmigrations

# Vérifier les problèmes potentiels
python manage.py check
```

### Nettoyer les Sessions Expirées

```bash
python manage.py clearsessions
```

### Réinitialiser la Base de Données

⚠️ **ATTENTION : Cette opération supprime toutes les données !**

```bash
# Supprimer la base de données
del db.sqlite3

# Recréer les tables
python manage.py migrate

# Recréer le superutilisateur
python manage.py createsuperuser
```
