from django.core.management.base import BaseCommand
from library.models import Book
from datetime import datetime


class Command(BaseCommand):
    help = 'Charge les livres initiaux dans la base de données'

    def handle(self, *args, **kwargs):
        books_data = [
            {
                'title': '1984',
                'author': 'George Orwell',
                'published_date': '1949-06-08',
                'category': 'Roman dystopique',
                'isbn': '9780451524935',
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'published_date': '1960-07-11',
                'category': 'Roman classique',
                'isbn': '9780061120084',
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'published_date': '1951-07-16',
                'category': 'Roman initiatique',
                'isbn': '9780316769488',
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'published_date': '1813-01-28',
                'category': 'Romance',
                'isbn': '9781503290563',
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'published_date': '1925-04-10',
                'category': 'Roman moderne',
                'isbn': '9780743273565',
            },
            {
                'title': "Harry Potter and the Philosopher's Stone",
                'author': 'J.K. Rowling',
                'published_date': '1997-06-26',
                'category': 'Fantasy',
                'isbn': '9780747532699',
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'published_date': '1988-04-15',
                'category': 'Philosophie / Fiction',
                'isbn': '9780061122415',
            },
            {
                'title': "Allah n'est pas obligé",
                'author': 'Ahmadou Kourouma',
                'published_date': '2000-05-04',
                'category': 'Roman africain',
                'isbn': '9782070416808',
            },
            {
                'title': 'Les Soleils des indépendances',
                'author': 'Ahmadou Kourouma',
                'published_date': '1970-01-01',
                'category': 'Roman politique',
                'isbn': '9782070377000',
            },
            {
                'title': 'Le vieux nègre et la médaille',
                'author': 'Ferdinand Oyono',
                'published_date': '1956-01-01',
                'category': 'Roman colonial',
                'isbn': '9782070363126',
            },
            {
                'title': 'Une si longue lettre',
                'author': 'Mariama Bâ',
                'published_date': '1979-01-01',
                'category': 'Roman épistolaire',
                'isbn': '9782266023167',
            },
            {
                'title': 'Le devoir de violence',
                'author': 'Yambo Ouologuem',
                'published_date': '1968-01-01',
                'category': 'Roman historique',
                'isbn': '9782070378236',
            },
            {
                'title': 'Blé de misère',
                'author': 'Bernard Dadié',
                'published_date': '1956-01-01',
                'category': 'Nouvelles africaines',
                'isbn': '9782708702362',
            },
            {
                'title': 'Climbié',
                'author': 'Bernard Dadié',
                'published_date': '1956-01-01',
                'category': 'Roman autobiographique',
                'isbn': '9782708702355',
            },
        ]

        created_count = 0
        updated_count = 0

        for book_data in books_data:
            book, created = Book.objects.update_or_create(
                isbn=book_data['isbn'],
                defaults={
                    'title': book_data['title'],
                    'author': book_data['author'],
                    'published_date': book_data['published_date'],
                    'category': book_data['category'],
                    'available': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Cree: {book.title}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[MAJ] Mis a jour: {book.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTermine! {created_count} livre(s) cree(s), {updated_count} livre(s) mis a jour.'
            )
        )
