import datetime

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.models import Book, Author, BookInstance
from catalog.forms import RenewBookForm


@login_required
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.
    
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0) + 1
    request.session['num_visits'] = num_visits
    
    context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_visits': num_visits,
        }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context=context)

class BookListView(generic.ListView):
    """Generic class-based view listing books."""
    model = Book
    paginate_by = 10 # Number of books to display per page
    # template_name = 'book_list.html' # Specify your own template name/location
    # context_object_name = 'book_list' # Specify your own context object name (default is object_list)
    
    # def get_queryset(self):
    #     """Return the list of books ordered by title."""
    #     return Book.objects.order_by('title')[:5] # Return the first 5 books ordered by title

class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book
    # template_name = 'book_detail.html' # Specify your own template name/location
    # context_object_name = 'book' # Specify your own context object name (default is object)
    
    # def get_context_data(self, **kwargs):
    #     """Add additional context data to the template."""
    #     context = super().get_context_data(**kwargs)
    #     context['book_instances'] = BookInstance.objects.filter(book=self.object).order_by('due_back')
    #     return context

class AuthorListView(generic.ListView):
    """Generic class-based view listing authors."""
    model = Author
    paginate_by = 10 # Number of authors to display per page
    # template_name = 'author_list.html' # Specify your own template name/location
    # context_object_name = 'author_list' # Specify your own context object name (default is object_list)
    
    # def get_queryset(self):
    #     """Return the list of authors ordered by last name."""
    #     return Author.objects.order_by('last_name')[:5] # Return the first 5 authors ordered by last name

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author
    # template_name = 'author_detail.html' # Specify your own template name/location
    # context_object_name = 'author' # Specify your own context object name (default is object)
    
    # def get_context_data(self, **kwargs):
    #     """Add additional context data to the template."""
    #     context = super().get_context_data(**kwargs)
    #     context['books'] = Book.objects.filter(author=self.object).order_by('title')
    #     return context

class LoanedBookByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10 # Number of books to display per page

    def get_queryset(self):
        """Return the list of books on loan to the current user."""
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    

class LoanedAllBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_librarian.html'
    paginate_by = 10 # Number of books to display per page
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        """Return the list of books on loan to the current user."""
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function to renew a specific book instance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    # If this is a POST request, we need to process the form data
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    
    # If this is a GET (or any other method), create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'due_back': proposed_renewal_date})
    
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    """Generic class-based view for creating a new author."""
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '05/01/2023'}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    """Generic class-based view for updating an existing author."""
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    """Generic class-based view for deleting an existing author."""
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )
        
class BookCreate(PermissionRequiredMixin, CreateView):
    """Generic class-based view for creating a new book."""
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    """Generic class-based view for updating an existing book."""
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.change_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    """Generic class-based view for deleting an existing book."""
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )