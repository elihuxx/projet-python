# Mémo de révision – Projet Bibliothèque en ligne

Ce mémo est fait pour t’aider à expliquer le projet à l’oral :
- ce que fait l’application
- comment elle est structurée
- quelles classes et vues sont importantes
- où sont codées les règles métier (emprunts, prolongements, retards)

---

## 1. Objectif général du projet

Application de **bibliothèque hybride** (physique + numérique) développée avec **Django** :
- Les livres sont des livres physiques stockés dans la bibliothèque.
- Le site permet aux **lecteurs** de :
  - s’inscrire, se connecter
  - consulter le catalogue
  - voir leurs emprunts
  - emprunter un livre disponible
  - demander un prolongement dans une fenêtre précise
  - rendre un livre
- Les **bibliothécaires (staff)** disposent d’un **dashboard `/gestion`** pour :
  - voir les statistiques
  - gérer les emprunts/retours
  - traiter les demandes de prolongement
  - rechercher livres, emprunts et lecteurs.

---

## 2. Architecture des dossiers

À connaître pour l’oral :

- **`mon_projet/`** : configuration Django
  - `settings.py` : configuration globale (BD, apps, middleware, templates)
  - `urls.py` : inclusion des URLs de l’app `library`

- **`library/`** : application principale
  - `models.py` : modèles métier `Book`, `User`, `Emprunts`, `DemandeProlongement`
  - `forms.py` : formulaires `RegisterForm`, `LoginForm`, `EmpruntForm`
  - `views.py` : vues publiques (home, catalogue, profil, etc.) + vues staff (`/gestion/...`)
  - `urls.py` : routes nommées pour toutes les vues
  - `templates/library/` : templates HTML (public + admin)
  - `admin.py` : configuration de l’admin Django

- **`docs/`** : documentation détaillée (pour le prof / la correction)

- **Racine**
  - `manage.py` : script de gestion Django
  - `db.sqlite3` : base de données SQLite
  - `README_DIAG.md` : infos pour les diagrammes UML
  - `README_MEMO.md` (ce fichier) : mémo de révision

---

## 3. Modèles principaux (diagramme de classes en pratique)

Les modèles sont dans **`library/models.py`**.

### 3.1. `Book`

**Rôle :** représenter un livre dans le catalogue.

Champs importants :
- `title`, `author`, `published_date`, `category`, `isbn (unique)`
- `total_copies` : nombre d’exemplaires physiques

Propriétés :
- `available_copies` :
  - calcule `total_copies - nombre d’emprunts actifs` pour ce livre
  - un emprunt est actif si `date_retour IS NULL`
- `is_available` :
  - `True` si `available_copies > 0`

**Lien UML :** `Book 1 ─ 0..* Emprunts`

### 3.2. `User` (lecteur métier)

**Rôle :** profil du lecteur pour la bibliothèque (à ne pas confondre avec `DjangoUser`).

Champs :
- `name`, `email (unique)`
- `membership_date` : date d’inscription
- `extensions_this_month` : nombre de prolongements utilisés ce mois-ci
- `last_reset_date` : dernière date où le compteur mensuel a été remis à zéro

Méthodes / propriétés :
- `reset_monthly_extensions()` :
  - si le mois de `last_reset_date` ≠ mois courant ⇒ remet `extensions_this_month` à 0 et met `last_reset_date` à aujourd’hui
- `active_borrows_count` : nombre d’emprunts actifs (`Emprunts` sans `date_retour`)
- `can_borrow` : `True` si `active_borrows_count < 3`
- `remaining_extensions` :
  - appelle `reset_monthly_extensions()`
  - renvoie `5 - extensions_this_month`

### 3.3. `Emprunts`

**Rôle :** un emprunt d’un livre par un lecteur.

Champs :
- `book` : `ForeignKey(Book)`
- `user` : `ForeignKey(User)`
- `date_emprunt` : date/heure de l’emprunt
- `date_fin_prevue` : date de retour prévue
- `date_retour` : date/heure du retour réel (NULL si encore emprunté)
- `deja_prolonge` : booléen, indique si un prolongement a déjà été accordé

Logique métier :
- `save()` :
  - si c’est un **nouvel emprunt** et que `date_fin_prevue` est vide ⇒ fixe `date_fin_prevue = aujourd’hui + 7 jours`
- `is_active` : `True` si `date_retour IS NULL`
- `days_remaining` :
  - si pas actif ⇒ 0
  - sinon ⇒ `max(0, date_fin_prevue - date_du_jour)`
- `is_overdue` :
  - `True` si emprunt actif et `date_du_jour > date_fin_prevue`
- `can_extend` :
  - emprunt actif
  - pas déjà prolongé
  - `user.remaining_extensions > 0`
  - `days_remaining == 1` (fenêtre précise : quand il reste 1 jour)
- `extend()` :
  - vérifie `can_extend`, sinon `ValidationError`
  - ajoute 5 jours à `date_fin_prevue`
  - met `deja_prolonge = True`
  - incrémente `user.extensions_this_month`
- `return_book()` :
  - vérifie que l’emprunt est actif, sinon `ValidationError`
  - remplit `date_retour` avec `timezone.now()`

### 3.4. `DemandeProlongement`

**Rôle :** demande de prolongement d’un emprunt faite par le lecteur, traitée par un membre du staff.

Champs :
- `emprunt` : `ForeignKey(Emprunts)`
- `date_demande`
- `statut` : `'en_attente'`, `'approuvee'`, `'rejetee'`
- `motif_rejet` (optionnel)
- `date_traitement` (optionnel)
- `traite_par` : `ForeignKey(DjangoUser)` (utilisateur staff qui traite la demande)

Méthodes :
- `approuver(admin_user)` :
  - vérifie `statut == 'en_attente'`
  - vérifie `emprunt.can_extend`
  - appelle `emprunt.extend()`
  - passe le statut à `'approuvee'`, renseigne `date_traitement` et `traite_par`
- `rejeter(motif, admin_user)` :
  - vérifie `statut == 'en_attente'`
  - passe le statut à `'rejetee'`, stocke le motif et le staff

### 3.5. `DjangoUser`

- C’est le modèle standard Django pour l’authentification.
- On utilise **l’email comme username**.
- Les **bibliothécaires** sont des `DjangoUser` avec `is_staff = True`.
- Lors de l’inscription :
  - `RegisterForm` crée un `DjangoUser` + un `User` (lecteur) et relie logiquement les deux via l’email.

---

## 4. Formulaires importants (`library/forms.py`)

### 4.1. `RegisterForm`

- Hérite de `UserCreationForm` (Django).
- Champs ajoutés : `email`, `name`.
- Dans `save()` :
  - définit `user.username = email`
  - enregistre le `DjangoUser`.
- La vue `register` crée ensuite l’objet `LibraryUser` (`User` métier) correspondant.

### 4.2. `LoginForm`

- Champs : `email`, `password`.
- Utilisé dans la vue `login_view` pour appeler `authenticate(username=email, password=...)`.

### 4.3. `EmpruntForm` (staff, dashboard)

- Champs : `user` (lecteur), `book` (livre).
- Dans `__init__` :
  - la queryset de `book` est filtrée pour ne proposer que les livres `is_available == True`.
- Dans `clean()` :
  - vérifie `book.is_available` (sinon erreur).
  - vérifie `user.can_borrow` (sinon erreur si déjà 3 emprunts actifs).

Ce formulaire est utilisé dans :
- `admin_dashboard`
- `admin_emprunts` (bloc "Nouvel emprunt rapide")
- `admin_enregistrer_emprunt` (POST de validation)

---

## 5. Vues publiques principales (`library/views.py`)

### 5.1. `home`

- Si l’utilisateur est connecté :
  - récupère le `LibraryUser` par email
  - passe `user_name` au template d’accueil.

### 5.2. `register`

- GET : affiche `RegisterForm`.
- POST :
  - valide `RegisterForm` ⇒ crée un `DjangoUser` avec l’email comme username.
  - crée un `LibraryUser` (`User` métier) avec `name` et `email`.
  - connecte automatiquement le nouvel utilisateur.

### 5.3. `login_view`

- GET : affiche `LoginForm`.
- POST :
  - récupère `email` + `password`
  - `authenticate(username=email, password=password)`
  - si OK ⇒ `login()` et redirection.

### 5.4. `catalog`

- Charge tous les `Book`.
- Filtres :
  - recherche texte sur `title`, `author`, `category`
  - filtre par `category`
  - option pour ne voir que les livres disponibles (`book.is_available`)

### 5.5. `book_detail`

- Charge un `Book` par `id`.
- Si utilisateur connecté ⇒ charge `LibraryUser` et calcule :
  - `can_borrow` (booléen) et `borrow_message` (texte explicatif)
  - vérifie dans l’ordre :
    1. disponibilité du livre (`book.is_available`)
    2. limite de 3 emprunts (`library_user.can_borrow`)
    3. délai d’1 jour depuis le dernier retour du **même livre**
- Le template affiche un bouton "Emprunter" seulement si `can_borrow == True`.

### 5.6. `borrow_book`

- **Vue critique à connaître pour l’oral.**
- POST uniquement.
- Étapes :
  1. Charge le `Book` et le `LibraryUser`.
  2. Vérifie :
     - `book.is_available`
     - `library_user.can_borrow` (moins de 3 emprunts actifs)
     - délai d’1 jour depuis le dernier retour du même livre
  3. Crée un `Emprunts` (c’est `save()` qui fixe `date_fin_prevue` à J+7).
  4. Ajoute un message de succès avec la date de retour prévue.

### 5.7. `my_borrows`

- Liste :
  - `active_borrows` : emprunts actifs du lecteur
  - `history` : derniers emprunts retournés
- Affichage des jours restants, retard, etc.

### 5.8. `return_book`

- POST.
- Vérifie que l’emprunt appartient au lecteur connecté.
- Appelle `emprunt.return_book()`.
- Affiche un message de confirmation.

### 5.9. `profile`

- Affiche :
  - infos du lecteur (`library_user`)
  - nombre d’emprunts actifs (`active_borrows`) et historique récent
  - demandes de prolongement en attente pour les emprunts actifs
  - bloc texte "Règles d’utilisation" (explication métier claire pour l’utilisateur)

### 5.10. `demander_prolongement`

- POST depuis le profil sur un emprunt donné.
- Vérifie dans l’ordre :
  - emprunt appartient au lecteur
  - emprunt actif
  - pas déjà prolongé
  - `remaining_extensions > 0` (quota mensuel)
  - pas en retard (`is_overdue == False`)
  - `can_extend == True` (il reste exactement 1 jour)
  - aucune `DemandeProlongement` en attente pour cet emprunt
- Si tout est OK ⇒ crée une `DemandeProlongement` avec `statut = 'en_attente'`.

### 5.11. `terms`

- Page "Conditions d’utilisation" qui explique :
  - durée des emprunts, limite de 3, délai 1 jour
  - prolongement de 5 jours, 5 prolongements/mois
  - pas de retour automatique (retour manuel)
  - retards et restrictions possibles.

---

## 6. Vues staff / dashboard (`/gestion/...`)

### 6.1. Sécurité

Toutes ces vues sont décorées par `@login_required` **et** vérifient `request.user.is_staff`.

### 6.2. `admin_dashboard`

- URL : `/gestion/dashboard/`
- Calcule des statistiques avec les modèles :
  - nombre total de livres, nombre d’exemplaires, exemplaires disponibles
  - nombre de lecteurs
  - nombre d’emprunts actifs
- Récupère :
  - emprunts en retard (`date_fin_prevue < aujourd’hui`)
  - emprunts à rendre bientôt (≤ 2 jours)
  - demandes de prolongement en attente
  - formulaire `EmpruntForm` pour créer un emprunt rapide
- Template : `admin_dashboard.html` + base `admin_base.html` avec **sidebar claire**.

### 6.3. `admin_livres`

- URL : `/gestion/livres/`
- Recherche les livres par texte (titre, auteur, catégorie, ISBN).
- Permet au staff de visualiser rapidement le catalogue.

### 6.4. `admin_emprunts`

- URL : `/gestion/emprunts/`
- Filtres : statut (actifs, historique, tous).
- Recherche : titre du livre, nom/email du lecteur.
- Contient aussi un bloc "Nouvel emprunt rapide" avec `EmpruntForm` (mêmes validations métier que côté public).

### 6.5. `admin_utilisateurs`

- URL : `/gestion/utilisateurs/`
- Liste des lecteurs (`User` métier), recherche par nom ou email.
- Affiche le nombre d’emprunts actifs par lecteur.

### 6.6. `admin_enregistrer_emprunt`

- POST depuis les formulaires rapides du dashboard/onglet emprunts.
- Valide `EmpruntForm`.
- Crée l’`Emprunts` et affiche un message de succès.

### 6.7. `admin_enregistrer_retour`

- POST : enregistre un retour pour un emprunt donné.
- Appelle `emprunt.return_book()`.

---

## 7. Règles métier à connaître par cœur

1. **Limite d’emprunts actifs** :
   - max **3** par lecteur.
   - Implémenté via `User.can_borrow` + vérifications dans `borrow_book` et `EmpruntForm.clean`.

2. **Durée d’un emprunt** :
   - **7 jours**.
   - Fixée automatiquement dans `Emprunts.save()` lors de la création.

3. **Délai de réemprunt du même livre** :
   - après avoir rendu un livre, il faut attendre **1 jour** pour réemprunter le même titre.
   - Vérifié dans `book_detail` et `borrow_book`.

4. **Prolongement** :
   - un seul prolongement de **5 jours** par emprunt.
   - prolongement possible seulement quand il reste **exactement 1 jour** (`days_remaining == 1`).
   - limite : **5 prolongements par mois** par lecteur (`remaining_extensions`).
   - vérifications dans `Emprunts.can_extend` et `demander_prolongement`.

5. **Retards** :
   - un emprunt est en retard le lendemain de la date de fin prévue.
   - logique dans `Emprunts.is_overdue`.
   - utilisé pour afficher badges "EN RETARD" et alimenter le dashboard.

6. **Retour de livre** :
   - côté lecteur : `return_book` (POST), côté staff : `admin_enregistrer_retour`.
   - les deux appellent `Emprunts.return_book()`.

7. **Demandes de prolongement** :
   - créées par la vue `demander_prolongement`.
   - traitées côté staff via le modèle `DemandeProlongement` (`approuver` / `rejeter`).

---

## 8. Questions typiques à l’oral et réponses rapides

- **Q : Quelle est la différence entre `DjangoUser` et `User` ?**  
  **R :** `DjangoUser` gère l’authentification (login/mot de passe, droits staff) ; `User` est le lecteur métier dans la bibliothèque (nom, email, stats d’emprunts). On les relie par l’email.

- **Q : Où est codée la limite de 3 emprunts ?**  
  Dans `User.can_borrow` et utilisée dans `borrow_book` (côté public) et `EmpruntForm.clean` (côté staff).

- **Q : Comment est calculée la date de fin prévue d’un emprunt ?**  
  Dans `Emprunts.save()` : si nouvel emprunt, `date_fin_prevue = aujourd’hui + 7 jours`.

- **Q : Quelles sont les conditions pour prolonger un emprunt ?**  
  Emprunt actif, pas déjà prolongé, pas en retard, lecteur avec des prolongements restants, et `days_remaining == 1`.

- **Q : À quoi sert `DemandeProlongement` ?**  
  À gérer le workflow de demande de prolongement : le lecteur demande, le staff approuve ou rejette via ce modèle.

- **Q : Que fait le dashboard `/gestion/dashboard/` ?**  
  Affiche les stats, les emprunts en retard / bientôt dus, les demandes de prolongement, et fournit un formulaire rapide pour créer/retourner des emprunts.

- **Q : Comment est séparée l’interface lecteur et l’interface staff ?**  
  Par les URL (`/` vs `/gestion/...`), les décorateurs (`@login_required` + `is_staff`) et deux bases de templates (`base.html` pour public, `admin_base.html` pour staff).

---

Ce mémo te permet d’avoir une vue d’ensemble claire. Pour réviser :
1. Relis cette fiche.
2. Ouvre les fichiers `models.py`, `views.py`, `forms.py` et retrouve les éléments cités.
3. Entraîne-toi à raconter **un scénario complet** :
   - un lecteur s’inscrit, se connecte, emprunte un livre, le prolonge, le rend, puis un bibliothécaire voit ça dans le dashboard et traite une demande de prolongement.

---

## 9. Mini cours Django (pour quelqu’un qui n’a jamais codé)

### 9.1. Ce qu’est Django

- Django est un **framework web** en Python : il fournit une structure pour créer un site web complet sans tout réinventer.
- Idée clé :
  - Tu écris des **modèles** (classes Python) pour représenter tes données (livres, lecteurs, emprunts…).
  - Tu écris des **vues** (fonctions Python) qui répondent aux requêtes HTTP.
  - Tu écris des **templates HTML** pour afficher le résultat aux utilisateurs.

### 9.2. Le chemin d’une requête (de l’URL au HTML)

Pour n’importe quelle page du site :

1. L’utilisateur va sur une URL (ex : `/catalog/`).
2. Django regarde dans `urls.py` **quelle vue** doit répondre.
3. La **vue** (fonction Python) exécute la logique :
   - lire la base de données via les **modèles**
   - éventuellement utiliser un **formulaire**
   - préparer un **contexte** (données à afficher)
4. La vue appelle `render(request, 'template.html', context)`.
5. Django remplace les variables dans le template HTML et renvoie la page au navigateur.

Visuellement :

`Navigateur → URL → urls.py → view (views.py) → models.py / forms.py → template HTML → Navigateur`

### 9.3. Projet vs Application

- **Projet** : répertoire `mon_projet/` + `manage.py` + configuration globale.
- **Application** : répertoire `library/` (logique métier de la bibliothèque).
- On peut avoir plusieurs applications dans un projet, mais ici l’appli principale est `library`.

---

## 10. Extraits de code par fichier (avec explication)

Objectif : si tu pars de zéro, ces exemples te montrent **quoi écrire** et **pourquoi**.

### 10.1. Gestion des URLs

#### `mon_projet/urls.py` – relier le projet à l’application

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library.urls', namespace='library')),
]
```

- On importe `include` pour déléguer les URL de l’app `library`.
- La ligne `path('', include('library.urls', namespace='library'))` dit :
  - « Pour toutes les URL qui commencent par `/`, regarde dans `library/urls.py`. »

#### `library/urls.py` – URLs fonctionnelles

```python
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('catalog/', views.catalog, name='catalog'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('my-borrows/', views.my_borrows, name='my_borrows'),
    path('profile/', views.profile, name='profile'),
    path('profile/borrow/<int:borrow_id>/return/', views.return_book, name='return_book'),
    path('profile/emprunt/<int:emprunt_id>/prolonger/', views.demander_prolongement, name='demander_prolongement'),
    path('terms/', views.terms, name='terms'),

    # Espace staff /gestion
    path('gestion/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('gestion/livres/', views.admin_livres, name='admin_livres'),
    path('gestion/emprunts/', views.admin_emprunts, name='admin_emprunts'),
    path('gestion/utilisateurs/', views.admin_utilisateurs, name='admin_utilisateurs'),
    path('gestion/emprunts/enregistrer/', views.admin_enregistrer_emprunt, name='admin_enregistrer_emprunt'),
    path('gestion/emprunts/<int:emprunt_id>/retour/', views.admin_enregistrer_retour, name='admin_enregistrer_retour'),
]
```

À l’oral, tu peux expliquer : chaque `path()` fait le lien **URL → fonction vue**.

### 10.2. Modèles – `library/models.py`

Extrait simplifié du modèle `Emprunts` (sans tous les import) :

```python
class Emprunts(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_fin_prevue = models.DateField(null=True, blank=True)
    date_retour = models.DateTimeField(null=True, blank=True)
    deja_prolonge = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk and not self.date_fin_prevue:
            self.date_fin_prevue = (timezone.now() + timedelta(days=7)).date()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.date_retour is None
```

Ce qu’il faut retenir :
- Le modèle hérite de `models.Model`.
- Les champs décrivent les colonnes en base.
- La méthode `save()` surcharge la sauvegarde pour fixer automatiquement la date de fin.

### 10.3. Vues – `library/views.py`

Exemple : vue `borrow_book` (simplifiée pour l’explication) :

```python
@login_required
def borrow_book(request, book_id):
    from .models import Book, Emprunts
    from django.shortcuts import get_object_or_404
    from django.utils import timezone

    if request.method != 'POST':
        return redirect('library:catalog')

    book = get_object_or_404(Book, id=book_id)
    library_user = LibraryUser.objects.get(email=request.user.email)

    if not book.is_available:
        messages.error(request, "Aucun exemplaire disponible")
        return redirect('library:book_detail', book_id=book_id)

    if not library_user.can_borrow:
        messages.error(request, "Limite de 3 emprunts atteinte")
        return redirect('library:book_detail', book_id=book_id)

    # (vérification du délai d'un jour pour réemprunter le même livre...)

    emprunt = Emprunts.objects.create(book=book, user=library_user)
    messages.success(request, "Livre emprunté avec succès !")
    return redirect('library:my_borrows')
```

Idées clés à expliquer :
- `@login_required` : protège l’accès aux utilisateurs connectés.
- On vérifie toutes les règles métier **avant** de créer l’emprunt.
- `messages.success` / `messages.error` servent à afficher des messages en haut des pages.

### 10.4. Formulaires – `library/forms.py`

Exemple : `EmpruntForm` côté staff :

```python
class EmpruntForm(forms.Form):
    user = forms.ModelChoiceField(queryset=LibraryUser.objects.all())
    book = forms.ModelChoiceField(queryset=Book.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_ids = [b.id for b in Book.objects.all() if b.is_available]
        self.fields['book'].queryset = Book.objects.filter(id__in=available_ids)

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        book = cleaned_data.get('book')

        if user and book:
            if not book.is_available:
                raise forms.ValidationError("Aucun exemplaire disponible pour ce livre.")
            if not user.can_borrow:
                raise forms.ValidationError("Cet utilisateur a déjà 3 emprunts actifs.")
        return cleaned_data
```

À l’oral : ce formulaire applique **les mêmes règles** que celles côté lecteur, mais dans l’interface staff.

### 10.5. Templates – `library/templates/library/base.html`

Un template Django combine HTML et balises `{% ... %}` / `{{ ... }}` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>{% block title %}Bibliothèque en Ligne{% endblock %}</title>
    <!-- Liens CSS Bootstrap, Font Awesome, styles -->
</head>
<body>
    <nav class="navbar">
        <a class="navbar-brand" href="{% url 'library:home' %}">Lectura</a>
        {% if user.is_authenticated %}
            <a href="{% url 'library:catalog' %}">Catalogue</a>
            <a href="{% url 'library:my_borrows' %}">Mes emprunts</a>
        {% else %}
            <a href="{% url 'library:login' %}">Connexion</a>
        {% endif %}
    </nav>

    <div class="container main-content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

Points importants :
- `{% block title %}` et `{% block content %}` permettent aux autres pages de **hériter** de cette base et de remplacer seulement le contenu.
- `{% url 'library:home' %}` génère l’URL à partir du nom défini dans `urls.py`.
- `{% if user.is_authenticated %}` permet d’afficher un menu différent pour un utilisateur connecté.

### 10.6. Templates staff – `admin_base.html`

- Même principe que `base.html`, mais :
  - design adapté au staff (sidebar, stats…)
  - liens vers `/gestion/dashboard/`, `/gestion/livres/`, `/gestion/emprunts/`, `/gestion/utilisateurs/`.
- Les templates `admin_*.html` (dashboard, livres, emprunts, utilisateurs) héritent de cette base.

---

## 11. Comment tout reconstruire étape par étape (plan de haut niveau)

Si quelqu’un part de zéro, l’ordre logique est :

1. **Créer le projet Django**
   - `django-admin startproject mon_projet` puis `cd mon_projet`.
2. **Créer l’application `library`**
   - `python manage.py startapp library`.
3. **Déclarer l’app dans `mon_projet/settings.py`** (`INSTALLED_APPS`).
4. **Créer les modèles** dans `library/models.py` (`Book`, `User`, `Emprunts`, `DemandeProlongement`).
5. **Lancer les migrations**
   - `python manage.py makemigrations` puis `python manage.py migrate`.
6. **Configurer les URLs**
   - `mon_projet/urls.py` pour inclure `library.urls`.
   - `library/urls.py` pour définir toutes les routes.
7. **Coder les vues** dans `library/views.py`
   - d’abord les vues simples (`home`, `catalog`, `register`, `login_view`),
   - puis les vues métier (`book_detail`, `borrow_book`, `my_borrows`, `profile`, `demander_prolongement`).
8. **Créer les templates** dans `library/templates/library/`
   - base `base.html`, puis `home.html`, `catalog.html`, `book_detail.html`, etc.
9. **Ajouter les formulaires** (`forms.py`) et les utiliser dans les vues.
10. **Créer l’espace staff** `/gestion` avec `admin_base.html` et les vues `admin_*`.

En lisant **ce mémo + le code du projet**, quelqu’un qui n’a jamais codé a une feuille de route claire pour tout reproduire.
