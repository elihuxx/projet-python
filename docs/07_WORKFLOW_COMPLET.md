# Workflow Complet - Bibliothèque Numérique en Ligne

## 📋 Vue d'Ensemble

Cette bibliothèque numérique fonctionne avec un **système d'emprunt limité** : un livre peut avoir plusieurs exemplaires, mais chaque exemplaire ne peut être emprunté que par un seul utilisateur à la fois.

---

## 🎯 Règles Métier Essentielles

### Emprunt
- **Durée initiale** : 7 jours (1 semaine)
- **Retour automatique** : J+7 à 23h59 (fin du 7ème jour)
- **Exemplaires multiples** : Un livre peut avoir plusieurs copies disponibles
- **Limite simultanée** : **Maximum 3 livres** par utilisateur en même temps

### Prolongements
- **Durée de prolongement** : +5 jours après la fin de la période normale
- **Moment** : Possible jusqu'à J+6 (avant la fin de la période initiale)
- **Limite par emprunt** : 1 seul prolongement par emprunt
- **Quota mensuel** : 5 prolongements maximum par utilisateur par mois (mois calendaire)
- **Reset** : Le compteur se réinitialise le 1er de chaque mois

### Délai de Réemprunt
- **Après retour** : Attendre 1 jour avant de pouvoir réemprunter le même livre
- **S'applique à** : Retour anticipé ET retour automatique

---

## 👥 Acteurs du Système

### 1. Administrateur
**Rôle** : Gestion complète de la bibliothèque

**Permissions** :
- Créer et gérer les utilisateurs
- Ajouter, modifier, supprimer des livres
- Définir le nombre d'exemplaires par livre
- Voir les statistiques globales
- Gérer les emprunts manuellement si nécessaire

### 2. Lecteur (Utilisateur)
**Rôle** : Emprunter et lire des livres

**Permissions** :
- S'inscrire et se connecter
- Parcourir le catalogue
- Emprunter des livres (max 3 simultanés)
- Prolonger ses emprunts (max 5/mois)
- Rendre des livres avant la date prévue
- Consulter son historique

---

## 📖 Workflow 1 : Emprunt d'un Livre

### Scénario Standard

```
┌─────────────────────────────────────────────────────────┐
│ JOUR 0 : EMPRUNT                                        │
├─────────────────────────────────────────────────────────┤
│ 1. LECTEUR se connecte                                  │
│ 2. LECTEUR parcourt le catalogue                        │
│ 3. LECTEUR trouve "Harry Potter"                        │
│                                                          │
│ SYSTÈME vérifie :                                       │
│ ✓ Exemplaires disponibles ? (ex: 2/3 disponibles)      │
│ ✓ Lecteur a moins de 3 emprunts actifs ?               │
│ ✓ Lecteur n'a pas emprunté ce livre récemment ?        │
│   (délai de 1 jour respecté)                            │
│                                                          │
│ SI TOUT OK :                                            │
│ → Création de l'emprunt                                 │
│   - date_emprunt = 01/11/2025                           │
│   - date_fin_prevue = 08/11/2025 (J+7)                  │
│   - deja_prolonge = False                               │
│   - date_retour = NULL                                  │
│                                                          │
│ → Mise à jour du stock                                  │
│   - Exemplaires disponibles : 2 → 1                     │
│                                                          │
│ 4. LECTEUR peut maintenant lire le livre en ligne      │
└─────────────────────────────────────────────────────────┘
```

### Cas de Refus d'Emprunt

**Cas 1 : Plus d'exemplaires disponibles**
```
Livre "1984" : 3 exemplaires
- 3 emprunts en cours
- 0 disponible
→ Message : "Tous les exemplaires sont empruntés. Retour prévu le [date]"
→ Option : "Réserver" (fonctionnalité future)
```

**Cas 2 : Limite de 3 emprunts atteinte**
```
Lecteur a déjà 3 livres empruntés
→ Message : "Vous avez atteint la limite de 3 emprunts simultanés"
→ Action : Rendre un livre avant d'en emprunter un autre
```

**Cas 3 : Délai de 1 jour non respecté**
```
Lecteur a rendu "Le Petit Prince" hier (10/11)
Aujourd'hui = 11/11
→ Message : "Vous devez attendre jusqu'au 12/11 pour réemprunter ce livre"
```

---

## 🔄 Workflow 2 : Prolongement d'un Emprunt

### Scénario avec Prolongement

```
┌─────────────────────────────────────────────────────────┐
│ JOUR 0-6 : PÉRIODE DE LECTURE INITIALE                 │
├─────────────────────────────────────────────────────────┤
│ Jour 0 : Emprunt                                        │
│   - date_emprunt = 01/11                                │
│   - date_fin_prevue = 08/11                             │
│                                                          │
│ Jour 1-6 : LECTURE EN COURS                             │
│   → Bouton "Prolonger" visible et actif                 │
│   → Affichage : "Prolongements restants ce mois : 4/5"  │
│                                                          │
│ Jour 6 : LECTEUR clique sur "Prolonger"                 │
│                                                          │
│ SYSTÈME vérifie :                                       │
│ ✓ Pas encore prolongé pour cet emprunt ?               │
│ ✓ Quota mensuel non atteint ? (< 5)                    │
│ ✓ Avant J+7 ? (oui, on est à J+6)                      │
│                                                          │
│ SI TOUT OK :                                            │
│ → Prolongement accordé                                  │
│   - date_fin_prevue = 13/11 (08/11 + 5 jours)          │
│   - deja_prolonge = True                                │
│   - Quota mensuel : 5 → 4 restants                      │
│                                                          │
│ → Bouton "Prolonger" disparaît                          │
│ → Message : "Prolongement accordé jusqu'au 13/11"       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ JOUR 7-12 : PÉRIODE DE PROLONGEMENT                    │
├─────────────────────────────────────────────────────────┤
│ Jour 7-12 : LECTURE CONTINUE                            │
│   → Pas de nouveau prolongement possible                │
│   → Affichage : "Déjà prolongé pour cet emprunt"        │
│                                                          │
│ Jour 13 à 00h00 : RETOUR AUTOMATIQUE                   │
│   - date_retour = 13/11                                 │
│   - Exemplaires disponibles : +1                        │
│   - Livre retiré de "Mes emprunts"                      │
│                                                          │
│ Jour 14 : PEUT RÉEMPRUNTER                             │
│   - Délai de 1 jour respecté                            │
│   - deja_prolonge repasse à False pour nouvel emprunt   │
└─────────────────────────────────────────────────────────┘
```

### Cas de Refus de Prolongement

**Cas 1 : Déjà prolongé pour cet emprunt**
```
deja_prolonge = True
→ Message : "Vous avez déjà prolongé cet emprunt"
→ Bouton "Prolonger" désactivé
```

**Cas 2 : Quota mensuel atteint**
```
Prolongements ce mois : 5/5
→ Message : "Quota mensuel de prolongements atteint (5/5)"
→ Info : "Réinitialisé le 1er du mois prochain"
```

**Cas 3 : Trop tard (après J+6)**
```
Jour actuel = Jour 7 ou plus
→ Message : "Trop tard pour prolonger (après J+6)"
→ Info : "Le prolongement doit être demandé avant la fin de la période"
```

---

## 📥 Workflow 3 : Retour d'un Livre

### Cas 1 : Retour Anticipé (avant J+7)

```
┌─────────────────────────────────────────────────────────┐
│ RETOUR ANTICIPÉ                                         │
├─────────────────────────────────────────────────────────┤
│ Jour 0 : Emprunt (01/11)                                │
│ Jour 3 : LECTEUR clique sur "Rendre"                    │
│                                                          │
│ SYSTÈME :                                               │
│ → Enregistre le retour                                  │
│   - date_retour = 04/11                                 │
│                                                          │
│ → Libère l'exemplaire                                   │
│   - Exemplaires disponibles : +1                        │
│                                                          │
│ → Applique le délai de réemprunt                        │
│   - Peut réemprunter ce livre à partir du 05/11        │
│                                                          │
│ Jour 4 : DÉLAI DE RÉEMPRUNT                             │
│   → Message si tentative : "Attendre jusqu'au 05/11"    │
│                                                          │
│ Jour 5 : PEUT RÉEMPRUNTER                               │
│   → Bouton "Emprunter" actif pour ce livre             │
└─────────────────────────────────────────────────────────┘
```

### Cas 2 : Retour Automatique (J+7 à 23h59)

```
┌─────────────────────────────────────────────────────────┐
│ RETOUR AUTOMATIQUE                                      │
├─────────────────────────────────────────────────────────┤
│ Jour 0 : Emprunt (01/11)                                │
│ Jour 1-7 : Lecture                                      │
│                                                          │
│ Jour 7 à 23h59 : RETOUR AUTO (08/11)                   │
│                                                          │
│ SYSTÈME (tâche automatique) :                           │
│ → Parcourt tous les emprunts                            │
│ → Identifie ceux où date_fin_prevue = aujourd'hui      │
│ → Pour chaque emprunt :                                 │
│   - date_retour = 08/11                                 │
│   - Exemplaires disponibles : +1                        │
│   - Email de notification au lecteur                    │
│                                                          │
│ Jour 8 : DÉLAI DE RÉEMPRUNT                             │
│   → Peut réemprunter à partir du 09/11                  │
│                                                          │
│ Jour 9 : PEUT RÉEMPRUNTER                               │
│   → Nouveau cycle possible                              │
└─────────────────────────────────────────────────────────┘
```

---

## 👤 Workflow 4 : Inscription et Connexion

### Inscription

```
1. VISITEUR arrive sur le site
   ↓
2. VISITEUR clique sur "S'inscrire"
   ↓
3. VISITEUR remplit le formulaire :
   - Nom complet
   - Adresse email (unique)
   - Mot de passe
   ↓
4. SYSTÈME :
   - Vérifie que l'email n'existe pas déjà
   - Crée le compte utilisateur
   - Envoie email de confirmation (optionnel)
   ↓
5. LECTEUR peut maintenant se connecter
```

### Connexion

```
1. LECTEUR entre ses identifiants
   ↓
2. SYSTÈME vérifie :
   - Email existe ?
   - Mot de passe correct ?
   ↓
3. SI OK :
   - Session créée
   - Redirection vers le catalogue
   ↓
4. LECTEUR voit :
   - Catalogue complet
   - "Mes emprunts" (emprunts en cours)
   - "Mon profil" (historique, stats)
```

---

## 📚 Workflow 5 : Gestion des Exemplaires Multiples

### Exemple Concret

```
┌─────────────────────────────────────────────────────────┐
│ LIVRE : "Harry Potter et la Pierre Philosophale"       │
│ Nombre d'exemplaires : 3                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ÉTAT INITIAL                                            │
│ Exemplaires disponibles : 3/3                           │
│ Emprunts actifs : 0                                     │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│                                                          │
│ USER1 emprunte (10h00)                                  │
│ → Exemplaires disponibles : 2/3                         │
│ → Emprunts actifs : 1                                   │
│                                                          │
│ USER2 emprunte (11h00)                                  │
│ → Exemplaires disponibles : 1/3                         │
│ → Emprunts actifs : 2                                   │
│                                                          │
│ USER3 emprunte (14h00)                                  │
│ → Exemplaires disponibles : 0/3                         │
│ → Emprunts actifs : 3                                   │
│ → Statut : COMPLET (tous exemplaires empruntés)         │
│                                                          │
│ USER4 tente d'emprunter (15h00)                         │
│ → ❌ REFUSÉ                                             │
│ → Message : "Tous les exemplaires sont empruntés"       │
│ → Info : "Prochains retours prévus :"                   │
│   - USER1 : 17/11                                       │
│   - USER2 : 18/11                                       │
│   - USER3 : 21/11                                       │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│                                                          │
│ USER1 rend le livre (16/11)                             │
│ → Exemplaires disponibles : 1/3                         │
│ → Emprunts actifs : 2                                   │
│                                                          │
│ USER4 peut maintenant emprunter                         │
│ → Exemplaires disponibles : 0/3                         │
│ → Emprunts actifs : 3                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Workflow 6 : Gestion du Quota Mensuel

### Suivi des Prolongements

```
┌─────────────────────────────────────────────────────────┐
│ NOVEMBRE 2025 - Quota : 5 prolongements                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 05/11 : Prolongement livre A                            │
│ → Quota restant : 4/5                                   │
│                                                          │
│ 10/11 : Prolongement livre B                            │
│ → Quota restant : 3/5                                   │
│                                                          │
│ 15/11 : Prolongement livre C                            │
│ → Quota restant : 2/5                                   │
│                                                          │
│ 20/11 : Prolongement livre D                            │
│ → Quota restant : 1/5                                   │
│                                                          │
│ 25/11 : Prolongement livre E                            │
│ → Quota restant : 0/5                                   │
│ → ⚠️ QUOTA ATTEINT                                      │
│                                                          │
│ 28/11 : Tentative de prolongement livre F               │
│ → ❌ REFUSÉ                                             │
│ → Message : "Quota mensuel atteint (5/5)"               │
│ → Info : "Réinitialisé le 1er décembre"                 │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│                                                          │
│ 01/12 à 00h00 : RESET AUTOMATIQUE                      │
│ → Quota restant : 5/5                                   │
│ → Nouveau mois, nouveau quota                           │
└─────────────────────────────────────────────────────────┘
```

### Calcul du Quota

Le quota se calcule sur le **mois calendaire** :
- Compte tous les emprunts où `deja_prolonge = True`
- Filtre par `date_emprunt` dans le mois en cours
- Maximum : 5 prolongements

**Important** : Le quota compte les prolongements **utilisés**, pas les prolongements **disponibles**.

---

## 🔐 Workflow 7 : Administration

### Ajout d'un Livre

```
1. ADMIN se connecte à l'interface admin
   ↓
2. ADMIN clique sur "Ajouter un livre"
   ↓
3. ADMIN remplit :
   - Titre
   - Auteur
   - Date de publication
   - Catégorie
   - ISBN (unique)
   - Nombre d'exemplaires (ex: 3)
   ↓
4. SYSTÈME :
   - Crée le livre
   - Initialise exemplaires_disponibles = nombre_exemplaires
   ↓
5. Livre visible dans le catalogue pour tous les lecteurs
```

### Création d'un Utilisateur

```
1. ADMIN accède à "Utilisateurs"
   ↓
2. ADMIN clique sur "Ajouter un utilisateur"
   ↓
3. ADMIN remplit :
   - Nom
   - Email
   - Mot de passe temporaire
   ↓
4. SYSTÈME crée le compte
   ↓
5. ADMIN envoie les identifiants au lecteur
```

### Consultation des Statistiques

```
ADMIN voit :
- Nombre total de livres
- Nombre d'exemplaires disponibles
- Nombre d'emprunts actifs
- Emprunts par livre
- Utilisateurs les plus actifs
- Prolongements utilisés ce mois
```

---

## ⏰ Workflow 8 : Tâches Automatiques

### Retour Automatique (Cron Job)

```
CHAQUE JOUR à 23h59 :

1. SYSTÈME parcourt tous les emprunts actifs
   WHERE date_retour IS NULL
   
2. Pour chaque emprunt :
   IF date_fin_prevue = aujourd'hui :
      - date_retour = aujourd'hui
      - Exemplaires disponibles : +1
      - Email au lecteur : "Votre emprunt est terminé"
      
3. Logs des retours automatiques
```

### Reset du Quota Mensuel

```
CHAQUE 1er DU MOIS à 00h00 :

1. SYSTÈME réinitialise les compteurs
   - Aucune action sur la base de données
   - Le calcul se fait dynamiquement sur le mois en cours
   
2. Email aux utilisateurs (optionnel) :
   "Votre quota de prolongements a été réinitialisé (5/5)"
```

---

## 📈 Cas d'Usage Complets

### Cas 1 : Cycle Complet avec Prolongement

```
01/11 : Emprunt "1984"
   - date_fin_prevue = 08/11
   - deja_prolonge = False
   
05/11 : Prolongement
   - date_fin_prevue = 13/11
   - deja_prolonge = True
   - Quota : 4/5 restants
   
13/11 23h59 : Retour auto
   - date_retour = 13/11
   
14/11 : Délai de réemprunt
   - Peut réemprunter à partir du 15/11
   
15/11 : Nouvel emprunt possible
   - deja_prolonge = False (nouveau cycle)
```

### Cas 2 : Retour Anticipé

```
01/11 : Emprunt "Le Petit Prince"
   - date_fin_prevue = 08/11
   
03/11 : Retour manuel
   - date_retour = 03/11
   - Pas de prolongement utilisé
   
04/11 : Délai de réemprunt
   - Peut réemprunter à partir du 05/11
   
05/11 : Peut réemprunter
```

### Cas 3 : Limite de 3 Emprunts

```
USER a 3 emprunts actifs :
- Livre A (retour prévu 10/11)
- Livre B (retour prévu 12/11)
- Livre C (retour prévu 15/11)

USER tente d'emprunter Livre D :
→ ❌ REFUSÉ
→ "Limite de 3 emprunts atteinte"

10/11 : Livre A retourné automatiquement
→ USER peut maintenant emprunter Livre D
```

---

## 🎯 Résumé des Contraintes

| Contrainte | Valeur | Reset |
|------------|--------|-------|
| Durée emprunt | 7 jours | Par emprunt |
| Prolongement | +5 jours | Par emprunt |
| Prolongements par emprunt | 1 maximum | Par emprunt |
| Quota prolongements | 5/mois | 1er du mois |
| Emprunts simultanés | 3 maximum | Temps réel |
| Délai réemprunt | 1 jour | Par livre |
| Retour automatique | J+7 à 23h59 | Par emprunt |

---

## 🔄 Diagramme de Flux Global

```
┌──────────────┐
│ INSCRIPTION  │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  CONNEXION   │
└──────┬───────┘
       │
       ↓
┌─────────────────────────────────────┐
│      PARCOURIR CATALOGUE            │
│  (Voir disponibilité par livre)     │
└──────┬──────────────────────────────┘
       │
       ↓
┌──────────────┐     ┌──────────────┐
│ Vérifications│────→│  EMPRUNTER   │
│ - Exemplaires│     │  (max 3)     │
│ - Limite 3   │     └──────┬───────┘
│ - Délai 1j   │            │
└──────────────┘            ↓
                     ┌──────────────┐
                     │ LIRE EN      │
                     │ LIGNE        │
                     └──────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ↓                           ↓
       ┌──────────────┐          ┌──────────────┐
       │ PROLONGER    │          │   RENDRE     │
       │ (J+0 à J+6)  │          │  (anticipé)  │
       │ Max 5/mois   │          └──────┬───────┘
       └──────┬───────┘                 │
              │                         │
              ↓                         │
       ┌──────────────┐                 │
       │ PÉRIODE      │                 │
       │ PROLONGÉE    │                 │
       │ (+5 jours)   │                 │
       └──────┬───────┘                 │
              │                         │
              ↓                         │
       ┌──────────────┐                 │
       │ RETOUR AUTO  │                 │
       │ J+7 ou J+12  │                 │
       └──────┬───────┘                 │
              │                         │
              └─────────┬───────────────┘
                        │
                        ↓
                 ┌──────────────┐
                 │ DÉLAI 1 JOUR │
                 └──────┬───────┘
                        │
                        ↓
                 ┌──────────────┐
                 │ DISPONIBLE   │
                 │ (réemprunt)  │
                 └──────────────┘
```

---

Ce workflow complet définit toutes les règles et processus de la bibliothèque numérique. Il servira de référence pour l'implémentation technique.
