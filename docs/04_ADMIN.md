# Documentation de l'Interface d'Administration

## Vue d'ensemble

L'interface d'administration Django fournit une interface web complète pour gérer les livres, les utilisateurs et les emprunts sans écrire de code supplémentaire.

## Configuration de l'Admin

### Fichier : `library/admin.py`

L'interface d'administration est configurée avec des fonctionnalités avancées pour chaque modèle.

---

## BookAdmin - Gestion des Livres

### Fonctionnalités

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'isbn',
        'total_copies', 'display_availability', 'published_date',
    )
    list_filter = ('category', 'published_date')
    search_fields = ('title', 'author', 'isbn')
    list_editable = ('total_copies',)
    readonly_fields = ('display_availability',)
```

### Détails des fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **list_display** | Colonnes affichées (dont `total_copies` et disponibilité colorée) |
| **list_filter** | Filtres disponibles dans la barre latérale |
| **search_fields** | Champs utilisables pour la recherche |
| **list_editable** | `total_copies` modifiable directement depuis la liste |

### Utilisation

1. **Ajouter un livre** :
   - Cliquez sur "Add Book"
   - Remplissez tous les champs obligatoires
   - Cliquez sur "Save"

2. **Rechercher un livre** :
   - Utilisez la barre de recherche en haut
   - Recherchez par titre, auteur ou ISBN

3. **Filtrer les livres** :
   - Utilisez les filtres dans la barre latérale droite
   - Filtrez par disponibilité, catégorie ou date de publication

4. **Voir rapidement la disponibilité** :
   - La colonne "Disponibilité" affiche "x/y disponible(s)" en vert ou en rouge selon le stock restant.

---

## UserAdmin - Gestion des Utilisateurs

### Fonctionnalités

```python
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'membership_date',
        'display_active_borrows', 'display_extensions',
    )
    search_fields = ('name', 'email')
    list_filter = ('membership_date',)
    readonly_fields = ('membership_date', 'display_active_borrows', 'display_extensions')
```

### Détails des fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **list_display** | Affiche le nom, l'email, la date d'inscription, les emprunts actifs et les prolongements restants |
| **search_fields** | Recherche par nom ou email |
| **list_filter** | Filtre par date d'inscription |

### Utilisation

1. **Ajouter un utilisateur** :
   - Cliquez sur "Add User"
   - Entrez le nom et l'email
   - La date d'inscription est automatiquement générée

2. **Rechercher un utilisateur** :
   - Utilisez la barre de recherche
   - Recherchez par nom ou email

3. **Filtrer par date d'inscription** :
   - Utilisez le filtre dans la barre latérale

---

## EmpruntsAdmin - Gestion des Emprunts

### Fonctionnalités

```python
@admin.register(Emprunts)
class EmpruntsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'book', 'date_emprunt', 'date_fin_prevue',
        'display_status', 'deja_prolonge', 'date_retour',
    )
    list_filter = ('deja_prolonge', 'date_emprunt', 'date_fin_prevue')
    search_fields = ('user__name', 'book__title')
    date_hierarchy = 'date_emprunt'
    readonly_fields = ('date_emprunt', 'display_status', 'display_days_remaining')
    actions = ['return_selected_books', 'extend_selected_borrows']
```

### Détails des fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **list_display** | Affiche l'utilisateur, le livre, les dates, le statut et l'indicateur de prolongement |
| **list_filter** | Filtre par prolongement et par dates |
| **search_fields** | Recherche par nom d'utilisateur ou titre de livre |
| **date_hierarchy** | Navigation par date d'emprunt (année/mois/jour) |
| **actions** | Actions groupées pour retourner ou prolonger plusieurs emprunts |

### Utilisation

1. **Enregistrer un emprunt** :
   - Cliquez sur "Add Emprunts"
   - Sélectionnez l'utilisateur et le livre
   - La date d'emprunt est automatiquement générée
   - Laissez la date de retour vide

2. **Enregistrer un retour** :
   - Trouvez l'emprunt dans la liste
   - Cliquez dessus pour l'éditer
   - Ajoutez la date de retour
   - Cliquez sur "Save"
   - La disponibilité du livre est recalculée automatiquement à partir des emprunts actifs.

3. **Rechercher un emprunt** :
   - Recherchez par nom d'utilisateur ou titre de livre

4. **Filtrer les emprunts** :
   - Filtrez par date d'emprunt ou de retour
   - Utilisez la hiérarchie de dates en haut de la page

5. **Voir les emprunts en cours** :
   - Filtrez par "Date retour: Unknown" pour voir les emprunts non retournés

---

## DemandeProlongementAdmin - Gestion des Demandes de Prolongement

### Fonctionnalités

```python
@admin.register(DemandeProlongement)
class DemandeProlongementAdmin(admin.ModelAdmin):
    list_display = ('emprunt', 'get_user', 'statut', 'date_demande')
    list_filter = ('statut', 'date_demande')
    search_fields = ('emprunt__book__title', 'emprunt__user__name')
```

### Détails des fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **list_display** | Affiche l'emprunt, l'utilisateur, le statut et la date de demande |
| **list_filter** | Filtre par statut et date de demande |
| **search_fields** | Recherche par titre de livre ou nom d'utilisateur |

### Utilisation

1. **Voir les demandes de prolongement** :
   - Allez dans "DemandeProlongement"
   - Recherchez par titre de livre ou nom d'utilisateur

2. **Traiter une demande de prolongement** :
   - Cliquez sur la demande
   - Modifiez le statut
   - Cliquez sur "Save"

---

## Accès à l'Interface d'Administration

### URL
```
http://127.0.0.1:8000/admin/
```

### Connexion

1. Démarrez le serveur :
   ```bash
   python manage.py runserver
   ```

2. Ouvrez votre navigateur et allez à l'URL ci-dessus

3. Connectez-vous avec vos identifiants de superutilisateur

### Créer un Superutilisateur

Si vous n'avez pas encore de compte administrateur :

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte.

---

## Workflow Typique

### Scénario : Emprunt d'un livre

1. **Vérifier la disponibilité du livre** :
   - Allez dans "Books"
   - Recherchez le livre
   - Vérifiez que "Available" est coché

2. **Créer l'emprunt** :
   - Allez dans "Emprunts"
   - Cliquez sur "Add Emprunts"
   - Sélectionnez l'utilisateur et le livre
   - Sauvegardez

3. **Marquer le livre comme indisponible** :
   - Retournez dans "Books"
   - Trouvez le livre
   - Décochez "Available"
   - Sauvegardez

### Scénario : Retour d'un livre

1. **Trouver l'emprunt** :
   - Allez dans "Emprunts"
   - Recherchez par nom d'utilisateur ou titre de livre
   - Ou filtrez les emprunts sans date de retour

2. **Enregistrer le retour** :
   - Cliquez sur l'emprunt
   - Ajoutez la date de retour (aujourd'hui)
   - Sauvegardez

3. **Marquer le livre comme disponible** :
   - Allez dans "Books"
   - Trouvez le livre
   - Cochez "Available"
   - Sauvegardez

---

## Conseils d'Utilisation

### Bonnes Pratiques

1. **Toujours vérifier la disponibilité** avant de créer un emprunt
2. **Mettre à jour la disponibilité** après chaque emprunt ou retour
3. **Utiliser la recherche** pour trouver rapidement des éléments
4. **Utiliser les filtres** pour analyser les données

### Raccourcis Utiles

- **Recherche rapide** : Utilisez Ctrl+F dans votre navigateur
- **Retour à la liste** : Cliquez sur le nom du modèle dans le fil d'Ariane
- **Actions en masse** : Sélectionnez plusieurs éléments et appliquez une action

### Limitations Actuelles

- La disponibilité du livre doit être mise à jour manuellement
- Pas de vérification automatique de la disponibilité lors de l'emprunt
- Pas de calcul automatique des retards

Ces fonctionnalités seront ajoutées dans les prochaines versions.
