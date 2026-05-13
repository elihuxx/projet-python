from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User as DjangoUser


class Book(models.Model):
    """Modèle représentant un livre dans la bibliothèque"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    author = models.CharField(max_length=100, verbose_name="Auteur")
    published_date = models.DateField(verbose_name="Date de publication")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    total_copies = models.IntegerField(default=1, verbose_name="Nombre d'exemplaires")
    
    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
        ordering = ['title']

    def __str__(self):
        return self.title
    
    @property
    def available_copies(self):
        """Retourne le nombre d'exemplaires disponibles"""
        emprunts_actifs = self.emprunts_set.filter(date_retour__isnull=True).count()
        return self.total_copies - emprunts_actifs
    
    @property
    def is_available(self):
        """Vérifie si au moins un exemplaire est disponible"""
        return self.available_copies > 0


class User(models.Model):
    """Modèle représentant un utilisateur de la bibliothèque"""
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(unique=True, verbose_name="Email")
    membership_date = models.DateField(auto_now_add=True, verbose_name="Date d'inscription")
    extensions_this_month = models.IntegerField(default=0, verbose_name="Prolongements ce mois")
    last_reset_date = models.DateField(default=timezone.now, verbose_name="Dernière réinitialisation")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def reset_monthly_extensions(self):
        """Réinitialise le compteur de prolongements si on est dans un nouveau mois"""
        today = timezone.now().date()
        if self.last_reset_date.month != today.month or self.last_reset_date.year != today.year:
            self.extensions_this_month = 0
            self.last_reset_date = today
            self.save()
    
    @property
    def active_borrows_count(self):
        """Retourne le nombre d'emprunts actifs"""
        return self.emprunts_set.filter(date_retour__isnull=True).count()
    
    @property
    def can_borrow(self):
        """Vérifie si l'utilisateur peut emprunter (max 3)"""
        return self.active_borrows_count < 3
    
    @property
    def remaining_extensions(self):
        """Retourne le nombre de prolongements restants ce mois"""
        self.reset_monthly_extensions()
        return 5 - self.extensions_this_month


class Emprunts(models.Model):
    """Modèle représentant un emprunt de livre"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Livre")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    date_emprunt = models.DateTimeField(auto_now_add=True, verbose_name="Date d'emprunt")
    date_fin_prevue = models.DateField(null=True, blank=True, verbose_name="Date de fin prévue")
    date_retour = models.DateTimeField(null=True, blank=True, verbose_name="Date de retour")
    deja_prolonge = models.BooleanField(default=False, verbose_name="Déjà prolongé")
    
    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
        ordering = ['-date_emprunt']

    def __str__(self):
        return f"{self.user.name} - {self.book.title}"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement la date de fin prévue si c'est un nouvel emprunt"""
        if not self.pk and not self.date_fin_prevue:
            self.date_fin_prevue = (timezone.now() + timedelta(days=7)).date()
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Vérifie si l'emprunt est actif (pas encore retourné)"""
        return self.date_retour is None
    
    @property
    def days_remaining(self):
        """Retourne le nombre de jours restants"""
        if not self.is_active or not self.date_fin_prevue:
            return 0
        delta = self.date_fin_prevue - timezone.now().date()
        return max(0, delta.days)
    
    @property
    def is_overdue(self):
        """Vérifie si l'emprunt est en retard"""
        if not self.is_active or not self.date_fin_prevue:
            return False
        return timezone.now().date() > self.date_fin_prevue
    
    @property
    def can_extend(self):
        """Vérifie si l'emprunt peut être prolongé"""
        if not self.is_active:
            return False
        if self.deja_prolonge:
            return False
        if self.user.remaining_extensions <= 0:
            return False
        # Prolongement possible uniquement entre J+6 et J+7 (quand il reste exactement 1 jour)
        return self.days_remaining == 1
    
    def extend(self):
        """Prolonge l'emprunt de 5 jours"""
        if not self.can_extend:
            raise ValidationError("Impossible de prolonger cet emprunt")
        
        self.date_fin_prevue = self.date_fin_prevue + timedelta(days=5)
        self.deja_prolonge = True
        self.user.extensions_this_month += 1
        self.user.save()
        self.save()
    
    def return_book(self):
        """Retourne le livre"""
        if not self.is_active:
            raise ValidationError("Ce livre a déjà été retourné")
        
        self.date_retour = timezone.now()
        self.save()


class DemandeProlongement(models.Model):
    """Modèle représentant une demande de prolongement d'emprunt"""
    STATUT_EN_ATTENTE = 'en_attente'
    STATUT_APPROUVEE = 'approuvee'
    STATUT_REJETEE = 'rejetee'

    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, 'En attente'),
        (STATUT_APPROUVEE, 'Approuvée'),
        (STATUT_REJETEE, 'Rejetée'),
    ]

    emprunt = models.ForeignKey(Emprunts, on_delete=models.CASCADE, verbose_name="Emprunt")
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE, verbose_name="Statut")
    motif_rejet = models.TextField(blank=True, null=True, verbose_name="Motif de rejet")
    date_traitement = models.DateTimeField(blank=True, null=True, verbose_name="Date de traitement")
    traite_par = models.ForeignKey(DjangoUser, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Traité par")

    class Meta:
        verbose_name = "Demande de prolongement"
        verbose_name_plural = "Demandes de prolongement"
        ordering = ['-date_demande']

    def __str__(self):
        return f"Demande de {self.emprunt.user.name} pour '{self.emprunt.book.title}'"

    def approuver(self, admin_user=None):
        """Approuve la demande et prolonge l'emprunt si possible"""
        if self.statut != self.STATUT_EN_ATTENTE:
            raise ValidationError("Cette demande a déjà été traitée")

        if not self.emprunt.can_extend:
            raise ValidationError("Impossible de prolonger cet emprunt")

        self.emprunt.extend()
        self.statut = self.STATUT_APPROUVEE
        self.date_traitement = timezone.now()
        if admin_user is not None:
            self.traite_par = admin_user
        self.save()

    def rejeter(self, motif, admin_user=None):
        """Rejette la demande avec un motif"""
        if self.statut != self.STATUT_EN_ATTENTE:
            raise ValidationError("Cette demande a déjà été traitée")

        self.statut = self.STATUT_REJETEE
        self.motif_rejet = motif
        self.date_traitement = timezone.now()
        if admin_user is not None:
            self.traite_par = admin_user
        self.save()
