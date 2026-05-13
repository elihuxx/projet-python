from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as DjangoUser
from .models import User as LibraryUser, Book, Emprunts


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription avec champs supplémentaires"""
    email = forms.EmailField(required=True, label="Email")
    name = forms.CharField(max_length=100, required=True, label="Nom complet")
    
    class Meta:
        model = DjangoUser
        fields = ['name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des labels
        self.fields['password1'].label = "Mot de passe"
        self.fields['password1'].help_text = "Votre mot de passe doit contenir au moins 8 caractères."
        self.fields['password2'].label = "Confirmation du mot de passe"
        self.fields['password2'].help_text = "Entrez le même mot de passe pour vérification."
        
        # Ajouter des classes CSS Bootstrap
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Utiliser l'email comme username
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Formulaire de connexion"""
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class EmpruntForm(forms.Form):
    """Formulaire d'enregistrement d'un emprunt (côté admin/dashboard)"""
    user = forms.ModelChoiceField(
        queryset=LibraryUser.objects.all(),
        label="Utilisateur",
        widget=forms.Select(attrs={
            'class': 'form-select select2-user',
        })
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        label="Livre",
        widget=forms.Select(attrs={
            'class': 'form-select select2-book',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ne proposer que les livres avec au moins un exemplaire disponible
        available_ids = [b.id for b in Book.objects.all() if b.is_available]
        self.fields['book'].queryset = Book.objects.filter(id__in=available_ids)

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        book = cleaned_data.get('book')

        if not user or not book:
            return cleaned_data

        # Vérifier disponibilité du livre
        if not book.is_available:
            raise forms.ValidationError("Aucun exemplaire disponible pour ce livre.")

        # Vérifier que l'utilisateur peut encore emprunter (max 3 actifs)
        if not user.can_borrow:
            raise forms.ValidationError("Cet utilisateur a déjà 3 emprunts actifs.")

        return cleaned_data
