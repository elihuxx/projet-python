from django.contrib import admin
from django.utils.html import format_html
from .models import Book, User, Emprunts, DemandeProlongement

# Bouton "Aller sur le site" dans l'admin Django -> dashboard de gestion
admin.site.site_url = '/gestion/dashboard/'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'isbn', 'total_copies', 'display_availability', 'published_date')
    list_filter = ('category', 'published_date')
    search_fields = ('title', 'author', 'isbn')
    list_editable = ('total_copies',)
    readonly_fields = ('display_availability',)
    
    def display_availability(self, obj):
        """Affiche la disponibilité avec couleur"""
        available = obj.available_copies
        total = obj.total_copies
        if available > 0:
            color = 'green'
            status = f'{available}/{total} disponible(s)'
        else:
            color = 'red'
            status = f'{available}/{total} (tous empruntés)'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    display_availability.short_description = 'Disponibilité'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'membership_date', 'display_active_borrows', 'display_extensions')
    search_fields = ('name', 'email')
    list_filter = ('membership_date',)
    readonly_fields = ('membership_date', 'display_active_borrows', 'display_extensions')
    
    def display_active_borrows(self, obj):
        """Affiche le nombre d'emprunts actifs"""
        count = obj.active_borrows_count
        color = 'red' if count >= 3 else 'green'
        return format_html(
            '<span style="color: {};">{}/3</span>',
            color, count
        )
    display_active_borrows.short_description = 'Emprunts actifs'
    
    def display_extensions(self, obj):
        """Affiche les prolongements restants"""
        remaining = obj.remaining_extensions
        color = 'red' if remaining == 0 else 'green'
        return format_html(
            '<span style="color: {};">{}/5 ce mois</span>',
            color, remaining
        )
    display_extensions.short_description = 'Prolongements'


@admin.register(Emprunts)
class EmpruntsAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'date_emprunt', 'date_fin_prevue', 'display_status', 'deja_prolonge', 'date_retour')
    list_filter = ('deja_prolonge', 'date_emprunt', 'date_fin_prevue')
    search_fields = ('user__name', 'book__title')
    date_hierarchy = 'date_emprunt'
    readonly_fields = ('date_emprunt', 'display_status', 'display_days_remaining')
    actions = ['return_selected_books', 'extend_selected_borrows']
    
    def display_status(self, obj):
        """Affiche le statut de l'emprunt avec couleur"""
        if not obj.is_active:
            return format_html('<span style="color: gray;">Retourné</span>')
        elif obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">EN RETARD</span>')
        elif obj.days_remaining <= 2:
            return format_html('<span style="color: orange;">Bientôt dû</span>')
        else:
            return format_html('<span style="color: green;">En cours</span>')
    display_status.short_description = 'Statut'
    
    def display_days_remaining(self, obj):
        """Affiche les jours restants"""
        if not obj.is_active:
            return 'N/A'
        days = obj.days_remaining
        if days == 0:
            return format_html('<span style="color: red;">Aujourd\'hui</span>')
        elif days < 0:
            return format_html('<span style="color: red;">{} jour(s) de retard</span>', abs(days))
        else:
            return f'{days} jour(s)'
    display_days_remaining.short_description = 'Jours restants'
    
    def return_selected_books(self, request, queryset):
        """Action pour retourner plusieurs livres"""
        count = 0
        for emprunt in queryset:
            if emprunt.is_active:
                emprunt.return_book()
                count += 1
        self.message_user(request, f'{count} livre(s) retourné(s) avec succès.')
    return_selected_books.short_description = 'Retourner les livres sélectionnés'
    
    def extend_selected_borrows(self, request, queryset):
        """Action pour prolonger plusieurs emprunts"""
        count = 0
        errors = 0
        for emprunt in queryset:
            if emprunt.can_extend:
                emprunt.extend()
                count += 1
            else:
                errors += 1
        self.message_user(request, f'{count} emprunt(s) prolongé(s). {errors} impossible(s) à prolonger.')
    extend_selected_borrows.short_description = 'Prolonger les emprunts sélectionnés'


@admin.register(DemandeProlongement)
class DemandeProlongementAdmin(admin.ModelAdmin):
    list_display = ('emprunt', 'get_user', 'statut', 'date_demande')
    list_filter = ('statut', 'date_demande')
    search_fields = ('emprunt__book__title', 'emprunt__user__name')

    def get_user(self, obj):
        return obj.emprunt.user
    get_user.short_description = 'Utilisateur'
