from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User as DjangoUser
from .forms import RegisterForm, LoginForm, EmpruntForm
from .models import User as LibraryUser


def home(request):
    """Page d'accueil"""
    context = {}
    
    # Si l'utilisateur est connecté, récupérer son profil LibraryUser
    if request.user.is_authenticated:
        try:
            library_user = LibraryUser.objects.get(email=request.user.email)
            context['user_name'] = library_user.name
        except LibraryUser.DoesNotExist:
            context['user_name'] = request.user.username
    
    return render(request, 'library/home.html', context)


def register(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('library:home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur Django
            django_user = form.save()
            
            # Créer l'utilisateur Library correspondant
            LibraryUser.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email']
            )
            
            # Connecter automatiquement l'utilisateur après inscription
            login(request, django_user)
            messages.success(request, f"Bienvenue {django_user.username} ! Votre compte a été créé avec succès.")
            return redirect('library:home')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()
    
    return render(request, 'library/register.html', {'form': form})


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('library:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Utiliser l'email comme username pour l'authentification
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue !")
                # Rediriger vers la page demandée ou la page d'accueil
                next_page = request.GET.get('next', 'library:home')
                return redirect(next_page)
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    
    return render(request, 'library/login.html', {'form': form})


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('library:home')


def catalog(request):
    """Vue du catalogue de livres"""
    from .models import Book
    from django.db.models import Q
    
    books = Book.objects.all()
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Filtre par catégorie
    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(category=category_filter)
    
    # Filtre par disponibilité
    available_only = request.GET.get('available', '')
    if available_only == 'true':
        # Filtrer les livres qui ont au moins un exemplaire disponible
        books = [book for book in books if book.is_available]
    
    # Récupérer toutes les catégories pour le filtre
    categories = Book.objects.values_list('category', flat=True).distinct().order_by('category')
    
    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'available_only': available_only,
    }
    
    return render(request, 'library/catalog.html', context)


def book_detail(request, book_id):
    """Vue de détails d'un livre"""
    from .models import Book, Emprunts
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from datetime import timedelta
    
    book = get_object_or_404(Book, id=book_id)
    
    context = {
        'book': book,
        'can_borrow': False,
        'borrow_message': '',
    }
    
    if request.user.is_authenticated:
        try:
            library_user = LibraryUser.objects.get(email=request.user.email)
            
            # Vérifier si l'utilisateur peut emprunter
            if not book.is_available:
                context['borrow_message'] = "Tous les exemplaires sont empruntés"
            elif not library_user.can_borrow:
                context['borrow_message'] = f"Vous avez atteint la limite de 3 emprunts simultanés ({library_user.active_borrows_count}/3)"
            else:
                # Vérifier le délai de 1 jour pour ce livre
                last_borrow = Emprunts.objects.filter(
                    user=library_user,
                    book=book
                ).order_by('-date_retour').first()
                
                if last_borrow and last_borrow.date_retour:
                    days_since_return = (timezone.now().date() - last_borrow.date_retour.date()).days
                    if days_since_return < 1:
                        next_date = last_borrow.date_retour.date() + timedelta(days=1)
                        context['borrow_message'] = f"Vous devez attendre jusqu'au {next_date.strftime('%d/%m/%Y')} pour réemprunter ce livre"
                    else:
                        context['can_borrow'] = True
                else:
                    context['can_borrow'] = True
            
            context['library_user'] = library_user
        except LibraryUser.DoesNotExist:
            context['borrow_message'] = "Profil utilisateur introuvable"
    
    return render(request, 'library/book_detail.html', context)


@login_required
def borrow_book(request, book_id):
    """Vue pour emprunter un livre"""
    from .models import Book, Emprunts
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from datetime import timedelta
    
    if request.method != 'POST':
        return redirect('library:catalog')
    
    book = get_object_or_404(Book, id=book_id)
    
    try:
        library_user = LibraryUser.objects.get(email=request.user.email)
    except LibraryUser.DoesNotExist:
        messages.error(request, "Profil utilisateur introuvable")
        return redirect('library:book_detail', book_id=book_id)
    
    # Vérifications
    if not book.is_available:
        messages.error(request, "Aucun exemplaire disponible")
        return redirect('library:book_detail', book_id=book_id)
    
    if not library_user.can_borrow:
        messages.error(request, f"Limite de 3 emprunts atteinte ({library_user.active_borrows_count}/3)")
        return redirect('library:book_detail', book_id=book_id)
    
    # Vérifier le délai de 1 jour
    last_borrow = Emprunts.objects.filter(
        user=library_user,
        book=book
    ).order_by('-date_retour').first()
    
    if last_borrow and last_borrow.date_retour:
        days_since_return = (timezone.now().date() - last_borrow.date_retour.date()).days
        if days_since_return < 1:
            next_date = last_borrow.date_retour.date() + timedelta(days=1)
            messages.error(request, f"Vous devez attendre jusqu'au {next_date.strftime('%d/%m/%Y')} pour réemprunter ce livre")
            return redirect('library:book_detail', book_id=book_id)
    
    # Créer l'emprunt
    emprunt = Emprunts.objects.create(
        book=book,
        user=library_user
    )
    
    messages.success(request, f"Livre emprunté avec succès ! À retourner le {emprunt.date_fin_prevue.strftime('%d/%m/%Y')}")
    return redirect('library:my_borrows')


@login_required
def my_borrows(request):
    """Vue des emprunts de l'utilisateur"""
    from .models import Emprunts
    
    try:
        library_user = LibraryUser.objects.get(email=request.user.email)
    except LibraryUser.DoesNotExist:
        messages.error(request, "Profil utilisateur introuvable")
        return redirect('library:home')
    
    # Emprunts actifs
    active_borrows = Emprunts.objects.filter(
        user=library_user,
        date_retour__isnull=True
    ).order_by('date_fin_prevue')
    
    # Historique (emprunts retournés)
    history = Emprunts.objects.filter(
        user=library_user,
        date_retour__isnull=False
    ).order_by('-date_retour')[:10]
    
    context = {
        'library_user': library_user,
        'active_borrows': active_borrows,
        'history': history,
    }
    
    return render(request, 'library/my_borrows.html', context)


@login_required
def demander_prolongement(request, emprunt_id):
    """Vue pour demander un prolongement d'emprunt"""
    from .models import Emprunts, DemandeProlongement
    from django.shortcuts import get_object_or_404

    if request.method != 'POST':
        return redirect('library:profile')

    try:
        library_user = LibraryUser.objects.get(email=request.user.email)
    except LibraryUser.DoesNotExist:
        messages.error(request, "Profil utilisateur introuvable")
        return redirect('library:profile')

    emprunt = get_object_or_404(Emprunts, id=emprunt_id)

    if emprunt.user != library_user:
        messages.error(request, "Cet emprunt ne vous appartient pas")
        return redirect('library:profile')

    if not emprunt.is_active:
        messages.error(request, "Cet emprunt n'est plus actif")
        return redirect('library:profile')

    if emprunt.deja_prolonge:
        messages.error(request, "Cet emprunt a déjà été prolongé")
        return redirect('library:profile')

    if emprunt.user.remaining_extensions <= 0:
        messages.error(request, "Vous avez atteint votre quota de prolongements pour ce mois")
        return redirect('library:profile')

    if emprunt.is_overdue:
        messages.error(request, "Impossible de demander un prolongement pour un emprunt en retard")
        return redirect('library:profile')

    if not emprunt.can_extend:
        messages.error(request, "Ce n'est pas encore le bon moment pour demander un prolongement")
        return redirect('library:profile')

    if DemandeProlongement.objects.filter(emprunt=emprunt, statut=DemandeProlongement.STATUT_EN_ATTENTE).exists():
        messages.error(request, "Une demande de prolongement est déjà en attente pour cet emprunt")
        return redirect('library:profile')

    DemandeProlongement.objects.create(emprunt=emprunt)

    messages.success(request, "Votre demande de prolongement a été envoyée et sera traitée par un bibliothécaire.")
    return redirect('library:profile')


@login_required
def return_book(request, borrow_id):
    """Vue pour retourner un livre (côté utilisateur)."""
    from .models import Emprunts
    from django.shortcuts import get_object_or_404

    if request.method != 'POST':
        return redirect('library:my_borrows')

    emprunt = get_object_or_404(Emprunts, id=borrow_id)

    try:
        library_user = LibraryUser.objects.get(email=request.user.email)
    except LibraryUser.DoesNotExist:
        messages.error(request, "Profil utilisateur introuvable")
        return redirect('library:my_borrows')

    if emprunt.user != library_user:
        messages.error(request, "Cet emprunt ne vous appartient pas")
        return redirect('library:my_borrows')

    try:
        emprunt.return_book()
        messages.success(request, f"Livre '{emprunt.book.title}' retourné avec succès")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('library:my_borrows')


@login_required
def profile(request):
    """Page de profil utilisateur"""
    from .models import Emprunts, DemandeProlongement

    try:
        library_user = LibraryUser.objects.get(email=request.user.email)
    except LibraryUser.DoesNotExist:
        messages.error(request, "Profil utilisateur introuvable")
        return redirect('library:home')

    active_borrows = Emprunts.objects.filter(user=library_user, date_retour__isnull=True).select_related('book')
    history = Emprunts.objects.filter(user=library_user, date_retour__isnull=False).order_by('-date_retour')[:10]

    pending_requests = DemandeProlongement.objects.filter(
        emprunt__in=active_borrows,
        statut=DemandeProlongement.STATUT_EN_ATTENTE,
    )
    pending_requests_ids = list(pending_requests.values_list('emprunt_id', flat=True))

    context = {
        'library_user': library_user,
        'active_borrows': active_borrows,
        'history': history,
        'pending_requests_ids': pending_requests_ids,
    }

    return render(request, 'library/profile.html', context)


def terms(request):
    """Page des conditions d'utilisation de la bibliothèque"""
    return render(request, 'library/terms.html')


@login_required
def admin_dashboard(request):
    """Dashboard administrateur (stats + emprunts/retours rapides)."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux comptes administrateurs.")
        return redirect('library:home')

    from django.utils import timezone
    from django.db.models import Sum
    from .models import Book, Emprunts, DemandeProlongement, User as LibraryUserModel

    today = timezone.now().date()

    total_books = Book.objects.count()
    aggregates = Book.objects.aggregate(total_copies=Sum('total_copies'))
    total_copies = aggregates['total_copies'] or 0
    available_copies = sum(book.available_copies for book in Book.objects.all())
    users_count = LibraryUserModel.objects.count()
    active_borrows_qs = Emprunts.objects.filter(date_retour__isnull=True)
    active_borrows_count = active_borrows_qs.count()

    overdue_borrows = active_borrows_qs.filter(date_fin_prevue__lt=today)
    due_soon_borrows = active_borrows_qs.filter(
        date_fin_prevue__gte=today,
        date_fin_prevue__lte=today + timezone.timedelta(days=2),
    )

    pending_requests = DemandeProlongement.objects.filter(
        statut=DemandeProlongement.STATUT_EN_ATTENTE
    ).select_related('emprunt__book', 'emprunt__user')

    emprunt_form = EmpruntForm()

    context = {
        'stats': {
            'total_books': total_books,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'users_count': users_count,
            'active_borrows': active_borrows_count,
        },
        'overdue_borrows': overdue_borrows.select_related('book', 'user')[:10],
        'due_soon_borrows': due_soon_borrows.select_related('book', 'user')[:10],
        'pending_requests': pending_requests[:10],
        'emprunt_form': emprunt_form,
        'active_borrows': active_borrows_qs.select_related('book', 'user')[:10],
    }

    return render(request, 'library/admin_dashboard.html', context)


@login_required
def admin_livres(request):
    """Liste et recherche des livres pour les comptes staff (gestion interne)."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux comptes administrateurs.")
        return redirect('library:home')

    from django.db.models import Q
    from .models import Book

    search = request.GET.get('q', '').strip()
    books = Book.objects.all().order_by('title')
    if search:
        books = books.filter(
            Q(title__icontains=search)
            | Q(author__icontains=search)
            | Q(category__icontains=search)
            | Q(isbn__icontains=search)
        )

    context = {
        'books': books,
        'search': search,
    }

    return render(request, 'library/admin_livres.html', context)


@login_required
def admin_emprunts(request):
    """Liste et recherche des emprunts pour les comptes staff."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux comptes administrateurs.")
        return redirect('library:home')

    from django.db.models import Q
    from .models import Emprunts
    from .forms import EmpruntForm

    statut = request.GET.get('statut', 'actifs')
    search = request.GET.get('q', '').strip()

    emprunt_form = EmpruntForm()

    emprunts_qs = Emprunts.objects.select_related('book', 'user').all()
    if statut == 'historique':
        emprunts_qs = emprunts_qs.filter(date_retour__isnull=False)
    elif statut == 'tout':
        pass
    else:
        emprunts_qs = emprunts_qs.filter(date_retour__isnull=True)

    if search:
        emprunts_qs = emprunts_qs.filter(
            Q(book__title__icontains=search)
            | Q(user__name__icontains=search)
            | Q(user__email__icontains=search)
        )

    context = {
        'emprunts': emprunts_qs.order_by('-date_emprunt'),
        'search': search,
        'statut': statut,
        'emprunt_form': emprunt_form,
    }

    return render(request, 'library/admin_emprunts.html', context)


@login_required
def admin_utilisateurs(request):
    """Liste et recherche des lecteurs de la bibliothèque pour les comptes staff."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux comptes administrateurs.")
        return redirect('library:home')

    from django.db.models import Q
    from .models import User as LibraryUserModel

    search = request.GET.get('q', '').strip()
    users = LibraryUserModel.objects.all().order_by('name')
    if search:
        users = users.filter(
            Q(name__icontains=search)
            | Q(email__icontains=search)
        )

    context = {
        'users': users,
        'search': search,
    }

    return render(request, 'library/admin_utilisateurs.html', context)


@login_required
def admin_enregistrer_emprunt(request):
    """Enregistre un nouvel emprunt depuis le dashboard admin."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux comptes administrateurs.")
        return redirect('library:home')

    from .models import Emprunts

    if request.method != 'POST':
        return redirect('library:admin_dashboard')

    form = EmpruntForm(request.POST)
    if form.is_valid():
        user = form.cleaned_data['user']
        book = form.cleaned_data['book']

        emprunt = Emprunts.objects.create(book=book, user=user)
        messages.success(
            request,
            f"Emprunt enregistré pour {user.name} : '{book.title}' (à rendre le {emprunt.date_fin_prevue.strftime('%d/%m/%Y')}).",
        )
    else:
        for error in form.non_field_errors():
            messages.error(request, error)

    return redirect('library:admin_dashboard')


@login_required
def admin_enregistrer_retour(request, emprunt_id):
    """Enregistre le retour d'un emprunt depuis le dashboard admin."""
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux comptes administrateurs.")
        return redirect('library:home')

    from .models import Emprunts
    from django.shortcuts import get_object_or_404

    if request.method != 'POST':
        return redirect('library:admin_dashboard')

    emprunt = get_object_or_404(Emprunts, id=emprunt_id)

    try:
        emprunt.return_book()
        messages.success(request, f"Retour enregistré pour '{emprunt.book.title}' ({emprunt.user.name}).")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('library:admin_dashboard')