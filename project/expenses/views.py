from django.forms import ValidationError
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            date = form.cleaned_data.get('date', '')
            end_date = form.cleaned_data.get('end_date', '')
            choices_category_list = form.cleaned_data.get('category_list', [])
            print('date', date)
            print('end_date', end_date)
            print('choices_category_list', choices_category_list)
           
            if date and end_date:
                queryset = queryset.filter(date__range=[date,end_date])

            # # Filter by end_date
            # if end_date:
            #     queryset = queryset.filter(date__lte=end_date)

            # Filter by categories
            if choices_category_list:
                queryset = queryset.filter(category__in=choices_category_list)

            # Filter by name
            if name:
                queryset = queryset.filter(name__icontains=name)


        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            **kwargs)
    def clean(self):
        cleaned_data = super().clean()

        # Check if end_date is greater than or equal to start_date
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if end_date and start_date and end_date < start_date:
            raise ValidationError(('End date must be greater than or equal to start date.'))
class CategoryListView(ListView):
    model = Category
    paginate_by = 5

