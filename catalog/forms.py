import datetime

from django import forms
from django.utils import timezone

from catalog.models import BookInstance

# class RenewBookForm(forms.Form):
#     """Form to renew a book."""
#     renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
    
#     def clean_renewal_date(self):
#         data = self.cleaned_data['renewal_date']
        
#         # Check if the date is in the past
#         if data < timezone.now().date():
#             raise forms.ValidationError('Invalid date - renewal in past')
        
#         # Check if the date is more than 4 weeks in the future
#         if data > timezone.now().date() + datetime.timedelta(weeks=4):
#             raise forms.ValidationError('Invalid date - renewal more than 4 weeks ahead')
        
#         # Return the cleaned data
#         return data
    
class RenewBookForm(forms.ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data['due_back']
        
        # Check if the date is in the past
        if data < timezone.now().date():
            raise forms.ValidationError('Invalid date - renewal in past')
        
        # Check if the date is more than 4 weeks in the future
        if data > timezone.now().date() + datetime.timedelta(weeks=4):
            raise forms.ValidationError('Invalid date - renewal more than 4 weeks ahead')
        
        # Return the cleaned data
        return data
    
    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': 'renewal date'}
        help_texts = {'due_back': 'Enter a date between now and 4 weeks (default 3).'}
        widgets = {
            'due_back': forms.DateInput(attrs={'type': 'date'}),}

