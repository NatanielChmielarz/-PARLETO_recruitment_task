import datetime
from django.forms import ValidationError
from django.views.generic.list import ListView
from django.db.models import Sum
from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category
from django.db.models.functions import ExtractYear, ExtractMonth

class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ExpenseSearchForm(self.request.GET)
        
        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            categories = form.cleaned_data.get('category_list', [])

            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])
            if start_date:
                if start_date and end_date:
                    queryset = queryset.filter(date__range=[start_date, end_date])
                else:    
                    queryset = queryset.filter(date__range=[start_date,datetime.datetime.now()])
            if end_date:
                if start_date and end_date:
                    queryset = queryset.filter(date__range=[start_date, end_date])
                else:
                    queryset = queryset.filter(date__range=["2000-01-01", end_date])
            if categories:
                queryset = queryset.filter(category__in=categories)
            if name:
                queryset = queryset.filter(name__icontains=name)
            sort_by = form.cleaned_data.get('sort_by')
            if sort_by == 'category_asc':
                queryset = queryset.order_by('category__name')
            elif sort_by == 'category_desc':
                queryset = queryset.order_by('-category__name')
            elif sort_by == 'date_asc':
                queryset = queryset.order_by('date')
            elif sort_by == 'date_desc':
                queryset = queryset.order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ExpenseSearchForm(self.request.GET)
        queryset = self.get_queryset()
        summart_copy  = self.get_queryset() 
        context['form'] = form
        context['summary_per_category'] = summary_per_category(queryset)
        context['total_spent'] = self.get_queryset().aggregate(total_spent=Sum('amount'))['total_spent'] or 0
        
        summary_per_year_month = summart_copy.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).values('year', 'month').annotate(
            total_amount=Sum('amount')
        ).order_by('-year', '-month')

        context['summary_per_year_month'] = summary_per_year_month
        return context
        

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if end_date and start_date and end_date < start_date:
            raise ValidationError(('End date must be greater than or equal to start date.'))
        
        
class CategoryListView(ListView):
    model = Category
    paginate_by = 5
    

    def get_queryset(self):
        queryset = super().get_queryset()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.get_queryset()

        category_expense_counts = {}
        for category in categories:
            category_expense_counts[category.name] = category.expense_set.count()

        
        context['category_data'] = [(category, category_expense_counts.get(category.name, "Brak danych")) for category in categories]
        return context
    

