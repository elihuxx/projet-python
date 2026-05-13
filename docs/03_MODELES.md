# Documentation des Modèles

## Vue d'ensemble

L'application utilise quatre modèles principaux pour gérer la bibliothèque hybride :
1. **Book** : Représente les livres et leurs exemplaires
2. **User** : Représente les utilisateurs/lecteurs de la bibliothèque
3. **Emprunts** : Représente les transactions d'emprunt
4. **DemandeProlongement** : Représente les demandes de prolongement d’emprunt faites par les lecteurs

## Modèle Book (Livre)

### Description
Le modèle `Book` représente un livre dans la bibliothèque avec toutes ses informations essentielles.

### Champs

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `title` | CharField | Titre du livre | Max 200 caractères |
| `author` | CharField | Nom de l'auteur | Max 100 caractères |
| `published_date` | DateField | Date de publication | Format: YYYY-MM-DD |
| `category` | CharField | Catégorie/Genre du livre | Max 100 caractères |
| `isbn` | CharField | Numéro ISBN | Max 13 caractères, unique |
| `total_copies` | IntegerField | Nombre total d'exemplaires | Défaut: 1 |

> Remarque : le champ booléen `available` de la version 1 a été remplacé par un **calcul dynamique** basé sur les emprunts actifs.

### Méthodes

- `__str__()` : Retourne le titre du livre

### Exemple de code

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    category = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.IntegerField(default=1)

    @property
    def available_copies(self):
        # nombre d'exemplaires encore disponibles
        ...

    @property
    def is_available(self):
        return self.available_copies > 0

    def __str__(self):
        return self.title
```

### Utilisation

```python
# Rechercher un livre
livre = Book.objects.get(isbn="9782070612758")

print(livre.available_copies, "/", livre.total_copies)
print("Disponible ?", livre.is_available)
```

---

## Modèle User (Utilisateur)

### Description
Le modèle `User` représente un lecteur inscrit à la bibliothèque.

### Champs

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `name` | CharField | Nom complet de l'utilisateur | Max 100 caractères |
| `email` | EmailField | Adresse email | Unique, format email valide |
| `membership_date` | DateField | Date d'inscription | Auto-généré à la création |

### Méthodes

- `__str__()` : Retourne le nom de l'utilisateur

### Exemple de code

```python
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    membership_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
```

### Utilisation

```python
# Créer un utilisateur
utilisateur = User.objects.create(
    name="Jean Dupont",
    email="jean.dupont@example.com"
)

# Rechercher un utilisateur
utilisateur = User.objects.get(email="jean.dupont@example.com")

# Lister tous les utilisateurs
tous_les_users = User.objects.all()
```

---

## Modèle Emprunts (Emprunt)

### Description
Le modèle `Emprunts` représente une transaction d'emprunt entre un utilisateur et un livre.

### Champs

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `book` | ForeignKey | Livre emprunté | Relation avec Book |
| `user` | ForeignKey | Utilisateur emprunteur | Relation avec User |
| `date_emprunt` | DateTimeField | Date/heure de l'emprunt | Auto-généré à la création |
| `date_retour` | DateTimeField | Date/heure de retour | Nullable, optionnel |
| `date_fin_prevue` | DateField | Date de fin prévue (J+7) | Calculée automatiquement |
| `deja_prolonge` | BooleanField | Indique si déjà prolongé | Défaut: False |

### Relations

- **book** : Relation Many-to-One avec `Book` (un livre peut avoir plusieurs emprunts)
- **user** : Relation Many-to-One avec `User` (un utilisateur peut avoir plusieurs emprunts)

### Méthodes

- `__str__()` : Retourne "Nom de l'utilisateur - Titre du livre"

### Exemple de code

```python
class Emprunts(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour = models.DateTimeField(null=True, blank=True)
    date_fin_prevue = models.DateField(null=True, blank=True)
    deja_prolonge = models.BooleanField(default=False)

    @property
    def is_active(self):
        return self.date_retour is None

    @property
    def days_remaining(self):
        # jours restants avant la date prévue
        ...

    @property
    def is_overdue(self):
        # True si l'emprunt est en retard
        ...

    @property
    def can_extend(self):
        # True si les conditions de prolongement sont remplies
        ...

    def __str__(self):
        return f"{self.user.name} - {self.book.title}"
```

### Utilisation

```python
# Créer un emprunt
emprunt = Emprunts.objects.create(
    book=livre,
    user=utilisateur
)

# Enregistrer un retour
emprunt.date_retour = datetime.now()
emprunt.save()

# Marquer le livre comme disponible
livre.available_copies += 1
livre.save()

# Lister tous les emprunts en cours (non retournés)
emprunts_en_cours = Emprunts.objects.filter(date_retour__isnull=True)
```

---

## Modèle DemandeProlongement (Demande de prolongement)

### Description
Le modèle `DemandeProlongement` représente une demande de prolongement d'emprunt faite par un lecteur.

### Champs

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `emprunt` | ForeignKey | Emprunt associé | Relation avec Emprunts |
| `date_demande` | DateTimeField | Date/heure de la demande | Auto-généré à la création |
| `raison` | CharField | Raison de la demande | Max 200 caractères |

### Relations

- **emprunt** : Relation Many-to-One avec `Emprunts` (un emprunt peut avoir plusieurs demandes de prolongement)

### Méthodes

- `__str__()` : Retourne "Nom de l'utilisateur - Titre du livre - Date de la demande"

### Exemple de code

```python
class DemandeProlongement(models.Model):
    emprunt = models.ForeignKey(Emprunts, on_delete=models.CASCADE)
    date_demande = models.DateTimeField(auto_now_add=True)
    raison = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.emprunt.user.name} - {self.emprunt.book.title} - {self.date_demande}"
```

### Utilisation

```python
# Créer une demande de prolongement
demande = DemandeProlongement.objects.create(
    emprunt=emprunt,
    raison="Besoin de plus de temps pour terminer la lecture"
)

# Lister toutes les demandes de prolongement
demandes = DemandeProlongement.objects.all()
```

---

## Relations entre les Modèles

```
User (1) ----< (N) Emprunts (N) >---- (1) Book
Emprunts (1) ----< (N) DemandeProlongement (N) >---- (1) Emprunts
```

- Un **utilisateur** peut avoir plusieurs **emprunts**
- Un **livre** peut avoir plusieurs **emprunts** (historique)
- Un **emprunt** est lié à un seul **utilisateur** et un seul **livre**
- Un **emprunt** peut avoir plusieurs **demandes de prolongement**

## Table de la Base de Données

Les modèles génèrent les tables suivantes dans SQLite :

- `library_book` : Table des livres (avec `total_copies`)
- `library_user` : Table des utilisateurs
- `library_emprunts` : Table des emprunts (avec `date_fin_prevue`, `deja_prolonge`, etc.)
- `library_demandeprolongement` : Table des demandes de prolongement

## Migrations

Pour appliquer les modèles à la base de données :

```bash
# Créer les fichiers de migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```
