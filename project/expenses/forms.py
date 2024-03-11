import datetime
from django import forms
from.models import Expense, Category

def get_category_list():
    cat_list = Category.objects.all()
    choices = [(obj.id, obj.name) for obj in cat_list]
    return choices
def get_years_list():
    years_list = list(range(2000, 2024))
    return years_list
class ExpenseSearchForm(forms.Form):
    name = forms.CharField(required=False)
    # date = forms.DateField(widget=forms.SelectDateWidget(years=get_years_list()))
    # end_date = forms.DateField(widget=forms.SelectDateWidget(years=get_years_list()))
    start_date = forms.DateField(widget=forms.DateInput())
    end_date = forms.DateField(widget=forms.DateInput())
    category_list = forms.MultipleChoiceField(
        choices=get_category_list(),
        widget=forms.CheckboxSelectMultiple(),
    )
    sort_by = forms.ChoiceField(choices=(
        ('','No sorting'),
        ('category_asc', 'Category (Ascending)'),
        ('category_desc', 'Category (Descending)'),
        ('date_asc', 'Date (Ascending)'),
        ('date_desc', 'Date (Descending)'),
        
    ), required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['category_list'].required = False
        self.fields['sort_by'].required = False
        
        
