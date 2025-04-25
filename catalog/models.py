from django.db import models
from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.contrib.auth.models import User
import uuid
from datetime import date

class Genre(models.Model):
    """Cet objet représente une catégorie ou un genre littéraire."""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
           Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet."""
        return self.name

class Book(models.Model):
    """Cet objet représente un livre (mais ne traite pas les copies présentes en rayon)."""
    title = models.CharField(max_length=200, help_text='Enter the book title')
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13 Character ISBN number')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
           Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet."""
        return self.title
    
    def get_absolute_url(self):
        """Retourne l'URL de la page de détail du livre."""
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        """Crée une chaîne de caractères pour le genre. Ce n'est pas nécessairement le meilleur moyen de faire cela, mais c'est un bon exemple."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = 'Genre'  # Renomme la colonne dans l'admin
    
class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
           Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet."""
        return f'{self.id} ({self.book.title})'
    
class Author(models.Model):
    """Cet objet représente un auteur."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
           Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet."""
        return f'{self.last_name}, {self.first_name}'
    
    def get_absolute_url(self):
        """Retourne l'URL de la page de détail de l'auteur."""
        return reverse('author-detail', args=[str(self.id)])
    
class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            unique=True,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def get_absolute_url(self):
        """Returns the url to access a particular language instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message = "Language already exists (case insensitive match)"
            ),
        ]