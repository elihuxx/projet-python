# Diagrammes UML – Bibliothèque en ligne

Ce fichier rassemble toutes les informations nécessaires pour construire :

- **Un diagramme de classes** (modèle métier principal)
- **Un diagramme de cas d’utilisation** (fonctionnement lecteur / bibliothécaire)

Toutes les informations ci-dessous sont basées sur le code effectif du projet (modèles, vues, règles métier).

---

## 1. Diagramme de classes

### 1.1. Vue d’ensemble

Classes principales du domaine (côté application bibliothèque) :

- **`Book`** (livre)
- **`User`** (lecteur métier, alias `library.models.User`)
- **`Emprunts`** (emprunt d’un livre)
- **`DemandeProlongement`** (demande de prolonger un emprunt)
- **`DjangoUser`** (utilisateur d’authentification, `django.contrib.auth.models.User`)

> Remarque : `User` (lecteur) et `DjangoUser` sont deux classes distinctes. Elles sont **liées logiquement par l’email**, pas par une ForeignKey.


### 1.2. Classe `Book` (`library.models.Book`)

**Rôle :** Représente un livre dans le catalogue.

**Attributs (champs persistés) :**
- `title: CharField(200)` – Titre du livre
- `author: CharField(100)` – Auteur
- `published_date: DateField` – Date de publication
- `category: CharField(100)` – Catégorie
- `isbn: CharField(13, unique=True)` – Code ISBN, unique
- `total_copies: IntegerField(default=1)` – Nombre total d’exemplaires physiques

**Propriétés dérivées :**
- `available_copies: int`
  - Calcule : `total_copies - emprunts_actifs`
  - `emprunts_actifs` = nombre d’objets `Emprunts` liés avec `date_retour IS NULL`
- `is_available: bool`
  - `True` si `available_copies > 0`

**Associations :**
- `Book 1  ─── 0..* Emprunts`
  - Côté `Emprunts` : `book = ForeignKey(Book, on_delete=CASCADE)`


### 1.3. Classe `User` (`library.models.User`) – Lecteur

**Rôle :** Représente un lecteur de la bibliothèque (profil métier lié à l’email).

**Attributs (champs persistés) :**
- `name: CharField(100)` – Nom complet
- `email: EmailField(unique=True)` – Email, unique
- `membership_date: DateField(auto_now_add=True)` – Date d’inscription
- `extensions_this_month: IntegerField(default=0)` – Nombre de prolongements déjà utilisés pour le mois courant
- `last_reset_date: DateField(default=timezone.now)` – Date du dernier reset mensuel

**Méthodes & propriétés :**
- `reset_monthly_extensions()`
  - Si le mois (ou l’année) de `last_reset_date` est différent de celui d’aujourd’hui : remet `extensions_this_month` à 0 et met à jour `last_reset_date`.
- `active_borrows_count: int` (property)
  - Nombre d’`Emprunts` liés avec `date_retour IS NULL`.
- `can_borrow: bool` (property)
  - `True` si `active_borrows_count < 3` (max 3 emprunts actifs).
- `remaining_extensions: int` (property)
  - Appelle `reset_monthly_extensions()` puis renvoie `5 - extensions_this_month`.

**Associations :**
- `User 1  ─── 0..* Emprunts`
  - Côté `Emprunts` : `user = ForeignKey(User, on_delete=CASCADE)`
- Relation **conceptuelle** 1–1 (non matérialisée) avec `DjangoUser` :
  - Lors de l’inscription, on crée un `DjangoUser` (auth) et un `User` (lecteur) avec le même email.


### 1.4. Classe `Emprunts` (`library.models.Emprunts`)

**Rôle :** Représente un emprunt d’un livre par un lecteur.

**Attributs (champs persistés) :**
- `book: ForeignKey(Book)` – Livre emprunté
- `user: ForeignKey(User)` – Lecteur emprunteur
- `date_emprunt: DateTimeField(auto_now_add=True)` – Date/heure de création de l’emprunt
- `date_fin_prevue: DateField(null=True, blank=True)` – Date prévue de retour
- `date_retour: DateTimeField(null=True, blank=True)` – Date/heure réelle de retour (NULL si encore actif)
- `deja_prolonge: BooleanField(default=False)` – Indique si l’emprunt a déjà été prolongé une fois

**Méthodes et propriétés métier :**
- `save()`
  - Si c’est un **nouvel emprunt** (`not self.pk`) et que `date_fin_prevue` est vide :
    - fixe `date_fin_prevue = aujourd’hui + 7 jours`.
- `is_active: bool` (property)
  - `True` si `date_retour IS NULL`.
- `days_remaining: int` (property)
  - Si l’emprunt n’est pas actif ou sans `date_fin_prevue` ⇒ `0`.
  - Sinon, `delta = date_fin_prevue - date_du_jour`, puis `max(0, delta.days)`.
- `is_overdue: bool` (property)
  - `True` si l’emprunt est encore actif **et** si `date_du_jour > date_fin_prevue`.
- `can_extend: bool` (property)
  - Conditions cumulatives :
    - Emprunt actif (`is_active`)
    - `deja_prolonge == False`
    - `user.remaining_extensions > 0`
    - `days_remaining == 1` (fenêtre de prolongement : quand il reste exactement 1 jour)
- `extend()`
  - Vérifie `can_extend` (sinon lève `ValidationError`).
  - Ajoute 5 jours à `date_fin_prevue`.
  - Met `deja_prolonge = True`.
  - Incrémente `user.extensions_this_month` et sauvegarde le `User`.
- `return_book()`
  - Si l’emprunt n’est pas actif ⇒ `ValidationError`.
  - Sinon, fixe `date_retour = maintenant` et sauvegarde.

**Associations :**
- Voir ci-dessus :
  - `Book 1 ─── 0..* Emprunts`
  - `User 1 ─── 0..* Emprunts`
- `Emprunts 1 ─── 0..* DemandeProlongement`
  - Côté `DemandeProlongement` : `emprunt = ForeignKey(Emprunts)`


### 1.5. Classe `DemandeProlongement` (`library.models.DemandeProlongement`)

**Rôle :** Représente une demande de prolongement d’un emprunt faite par un lecteur et traitée par le staff.

**Attributs (champs persistés) :**
- `emprunt: ForeignKey(Emprunts)` – Emprunt concerné
- `date_demande: DateTimeField(auto_now_add=True)` – Date/heure de la demande
- `statut: CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')`
  - Valeurs possibles :
    - `'en_attente'` – En attente de traitement
    - `'approuvee'` – Approuvée
    - `'rejetee'` – Rejetée
- `motif_rejet: TextField(blank=True, null=True)` – Raison du rejet (si applicable)
- `date_traitement: DateTimeField(blank=True, null=True)` – Date/heure de traitement
- `traite_par: ForeignKey(DjangoUser, null=True, blank=True, on_delete=SET_NULL)` – Staff ayant traité la demande

**Méthodes métier :**
- `approuver(admin_user=None)`
  - Vérifie que `statut == 'en_attente'`, sinon `ValidationError`.
  - Vérifie `emprunt.can_extend`, sinon `ValidationError`.
  - Appelle `emprunt.extend()`.
  - Met `statut = 'approuvee'`, `date_traitement = maintenant`, et éventuellement `traite_par = admin_user`.
- `rejeter(motif, admin_user=None)`
  - Vérifie que `statut == 'en_attente'`, sinon `ValidationError`.
  - Met `statut = 'rejetee'`, renseigne `motif_rejet`, `date_traitement` et `traite_par` si fourni.

**Associations :**
- `Emprunts 1 ─── 0..* DemandeProlongement`
- `DjangoUser 0..1 ─── 0..* DemandeProlongement` (via `traite_par`)


### 1.6. Classe `DjangoUser` (`django.contrib.auth.models.User`)

**Rôle :** Utilisateur technique pour l’authentification (login, permissions, `is_staff`).

**Utilisation dans le projet :**
- Les lecteurs se connectent avec un `DjangoUser` dont le `username` = email.
- Les bibliothécaires sont des `DjangoUser` avec `is_staff = True`.
- L’attribut `traite_par` de `DemandeProlongement` référence un `DjangoUser` staff.
- La correspondance avec `User` (lecteur métier) se fait par l’email (pas de FK).


---

## 2. Diagramme de cas d’utilisation

### 2.1. Acteurs

- **Lecteur**
  - Utilisateur authentifié (pair `DjangoUser` + `User` métier).
  - Rôle : consulter le catalogue, emprunter des livres, suivre ses emprunts, demander un prolongement, rendre un livre.

- **Bibliothécaire / Staff**
  - Utilisateur `DjangoUser` avec `is_staff = True`.
  - Rôle : gérer les livres, emprunts, retours, demandes de prolongement, et consulter le dashboard /gestion.

> Optionnel en UML : un acteur « Administrateur technique » (superutilisateur Django) pour l’installation, la configuration et la gestion de haut niveau.


### 2.2. Cas d’utilisation – Lecteur

Pour chaque cas, on indique les règles métier importantes.

1. **S’inscrire**  
   - Vue : `register`  
   - Acteur : Lecteur  
   - Préconditions : Non authentifié.  
   - Postconditions : Création d’un `DjangoUser` et d’un `User` (lecteur) avec le même email, connexion automatique.

2. **Se connecter / Se déconnecter**  
   - Vues : `login_view`, `logout_view`  
   - Acteur : Lecteur  
   - Règles : Authentification par email + mot de passe (email utilisé comme `username`).

3. **Consulter le catalogue**  
   - Vue : `catalog`  
   - Fonctions :
     - Afficher tous les `Book`.
     - Rechercher par titre / auteur / catégorie.
     - Filtrer par catégorie.
     - Filtrer par disponibilité (option « seulement les livres disponibles »).

4. **Voir les détails d’un livre**  
   - Vue : `book_detail`  
   - Règles métier côté affichage :
     - Si aucun exemplaire disponible ⇒ message « Tous les exemplaires sont empruntés ».
     - Si le lecteur a déjà 3 emprunts actifs ⇒ message indiquant la limite.
     - Si le lecteur a récemment rendu ce même livre (< 1 jour) ⇒ message indiquant la date à partir de laquelle il pourra réemprunter.
     - Sinon ⇒ bouton d’emprunt activé (`can_borrow = True`).

5. **Emprunter un livre**  
   - Vue : `borrow_book` (POST depuis `book_detail`)  
   - Préconditions :
     - Lecteur authentifié.
     - `book.is_available == True`.
     - `user.can_borrow == True` (moins de 3 emprunts actifs).
     - Délai d’1 jour respecté depuis le dernier retour du même livre (si existant).
   - Postconditions :
     - Création d’un `Emprunts` pour le couple (`User`, `Book`).
     - `date_fin_prevue` fixée à J+7 (si non renseignée).

6. **Consulter ses emprunts**  
   - Vues : `my_borrows`, section « Emprunts en cours » du `profile`  
   - Affiche :
     - Emprunts actifs (`date_retour IS NULL`) avec statut (jours restants, retard, déjà prolongé ou non).
     - Historique des derniers emprunts retournés.

7. **Rendre un livre**  
   - Vue : `return_book` (POST depuis `my_borrows`)  
   - Préconditions :
     - Emprunt appartient au lecteur connecté.
     - Emprunt encore actif.
   - Postconditions :
     - `date_retour` remplie avec la date/heure actuelle.
     - Le livre redevient disponible (via `Book.available_copies`).

8. **Consulter son profil**  
   - Vue : `profile`  
   - Affiche :
     - Informations lecteur (`name`, `email`, `membership_date`).
     - Compteurs : `active_borrows_count` / 3, `remaining_extensions` / 5.
     - Emprunts en cours, historique récent.
     - Règles d’utilisation en texte (emprunts, prolongements, retards, rôle des bibliothécaires).

9. **Demander un prolongement d’emprunt**  
   - Vue : `demander_prolongement` (POST depuis le profil, par emprunt)  
   - Préconditions métiers :
     - Emprunt appartient au lecteur.
     - Emprunt actif.
     - Pas déjà prolongé.
     - Pas en retard (`is_overdue == False`).
     - Lecteur a encore des prolongements disponibles (`remaining_extensions > 0`).
     - Fenêtre temporelle respectée (`emprunt.can_extend == True` ⇒ `days_remaining == 1`).
     - Aucune demande en attente existante pour cet emprunt.
   - Postconditions :
     - Création d’une `DemandeProlongement` avec `statut = 'en_attente'`.
     - Un bibliothécaire devra l’approuver ou la rejeter.

10. **Consulter les conditions d’utilisation**  
    - Vue : `terms`  
    - Cas d’utilisation de type « information » lié aux règles précédentes.


### 2.3. Cas d’utilisation – Bibliothécaire / Staff

1. **Accéder au dashboard de gestion**  
   - Vue : `admin_dashboard` (`/gestion/dashboard/`)  
   - Préconditions : `request.user.is_staff == True`.
   - Fonctions :
     - Voir les statistiques globales (livres, exemplaires disponibles, lecteurs, emprunts actifs).
     - Voir la liste des emprunts en retard.
     - Voir la liste des emprunts à rendre bientôt (≤ 2 jours).
     - Voir les demandes de prolongement en attente.

2. **Enregistrer un nouvel emprunt pour un lecteur (staff)**  
   - Vue : `admin_enregistrer_emprunt` (POST depuis le dashboard ou `/gestion/emprunts/`)  
   - Utilise le formulaire `EmpruntForm` (staff only).  
   - Règles :
     - Le champ `book` ne propose que les livres `is_available == True`.
     - Validation : livre disponible, lecteur avec moins de 3 emprunts actifs.
   - Postconditions : création d’un `Emprunts` comme pour un emprunt côté lecteur.

3. **Enregistrer un retour (staff)**  
   - Vue : `admin_enregistrer_retour` (POST depuis le dashboard)  
   - Actions : appelle `emprunt.return_book()` sur un `Emprunts` existant.

4. **Consulter / rechercher les livres (staff)**  
   - Vue : `admin_livres` (`/gestion/livres/`)  
   - Fonctions :
     - Rechercher par titre, auteur, catégorie, ISBN.
     - Voir la disponibilité (`Book.is_available`, `available_copies`).

5. **Consulter / rechercher les emprunts (staff)**  
   - Vue : `admin_emprunts` (`/gestion/emprunts/`)  
   - Fonctions :
     - Filtrer par statut : emprunts actifs, historique, tous.
     - Rechercher par titre de livre, nom ou email du lecteur.
     - Créer un emprunt rapide via `EmpruntForm`.

6. **Consulter / rechercher les lecteurs (staff)**  
   - Vue : `admin_utilisateurs` (`/gestion/utilisateurs/`)  
   - Fonctions :
     - Rechercher des lecteurs par nom ou email.
     - Visualiser le nombre d’emprunts actifs par lecteur.

7. **Traiter les demandes de prolongement**  
   - Interface : via l’administration Django sur `DemandeProlongement` (et/ou vues admin liées)  
   - Actions :
     - **Approuver** une demande ⇒ appelle `DemandeProlongement.approuver(admin_user)`.
     - **Rejeter** une demande ⇒ appelle `DemandeProlongement.rejeter(motif, admin_user)`.
   - Règles :
     - Uniquement si `statut == 'en_attente'`.
     - L’approbation ne peut se faire que si `emprunt.can_extend == True`.

8. **Gérer le catalogue et les paramètres avancés**  
   - Interface : Admin Django classique (`/admin/`)  
   - Acteur : Bibliothécaire / Administrateur technique
   - Permet :
     - CRUD complet sur `Book`, `User`, `Emprunts`, `DemandeProlongement`.
     - Gestion des comptes `DjangoUser` (dont droits `is_staff` / `is_superuser`).

---

## 3. Conseils pour dessiner les diagrammes

### 3.1. Diagramme de classes

- Représenter les classes : `Book`, `User`, `Emprunts`, `DemandeProlongement`, `DjangoUser`.
- Pour chaque classe :
  - Nom, attributs principaux, quelques méthodes/propriétés métier (celles listées ci-dessus).
- Associations recommandées :
  - `Book 1 ─── 0..* Emprunts`
  - `User 1 ─── 0..* Emprunts`
  - `Emprunts 1 ─── 0..* DemandeProlongement`
  - `DjangoUser 0..1 ─── 0..* DemandeProlongement` (via `traite_par`)
  - (Conceptuel) `DjangoUser 1 ─── 1 User` (liaison par email).
- Indiquer les contraintes métier dans des notes UML (par ex. « max 3 emprunts actifs », « days_remaining == 1 pour prolonger », etc.).

### 3.2. Diagramme de cas d’utilisation

- Acteurs principaux : **Lecteur**, **Bibliothécaire**.
- Cas d’utilisation à représenter (au minimum) :
  - Lecteur : S’inscrire, Se connecter, Consulter le catalogue, Consulter un livre, Emprunter un livre, Consulter ses emprunts, Rendre un livre, Demander un prolongement, Consulter son profil, Consulter les conditions d’utilisation.
  - Bibliothécaire : Accéder au dashboard, Enregistrer un emprunt, Enregistrer un retour, Gérer les livres, Gérer les emprunts, Gérer les lecteurs, Traiter les demandes de prolongement, Gérer le catalogue via l’admin.
- Vous pouvez utiliser des relations `<<include>>` / `<<extend>>` :
  - `Emprunter un livre` <<include>> `Consulter le détail d’un livre`.
  - `Demander un prolongement` <<extend>> `Consulter ses emprunts`.
  - `Enregistrer un emprunt (staff)` <<include>> `Sélectionner un lecteur` et `Sélectionner un livre`.

Ce fichier doit contenir tout ce qu’il faut pour dessiner proprement les deux diagrammes UML sans avoir à rouvrir le code.
