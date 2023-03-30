from django import forms
from .models import Drink, Sale,  Debt, Stock, ReduceStock

#  Defined Drink Form
class DrinkForm(forms.ModelForm):
    class Meta:
        model = Drink
        fields = ['name','category','price','image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            
        }

class StockForm(forms.ModelForm):
    drink = forms.ModelChoiceField(queryset=Drink.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
   

    class Meta:
        model = Stock
        fields = ['drink', 'quantity']


class ReduceStockForm(forms.ModelForm):
    drink = forms.ModelChoiceField(queryset=Drink.objects.all(), empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))
    total_reduction = forms.FloatField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ReduceStock
        fields = ['drink', 'total_reduction']

    def save(self, commit=True):
        instance = super(ReduceStockForm, self).save(commit=False)
        if commit:
            instance.drink.total_stock = instance.drink.total_stock() - self.cleaned_data['total_reduction']
            instance.drink.save()
            instance.save()
        return instance



#  Defined Sale Form
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['sale_date', 'drink', 'quantity', 'mode_of_payment', 'debtor_name', 'customer_name']
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'drink': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'mode_of_payment': forms.Select(attrs={'class': 'form-control'}),
            'debtor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['debtor_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['customer_name'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        mode_of_payment = cleaned_data.get('mode_of_payment')
        debtor_name = cleaned_data.get('debtor_name')
        customer_name = cleaned_data.get('customer_name')

        if mode_of_payment == 'DEBT' and not debtor_name:
            raise forms.ValidationError('Debtor name is required for debt transactions.')
        elif mode_of_payment == 'COMPLIMENTARY' and not customer_name:
            raise forms.ValidationError('Customer name is required for complimentary transactions.')
        
        return cleaned_data



#  Defined DebtForm
class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['debtor_name', 'amount', 'status']
        widgets = {
            'status': forms.Select(choices=Debt.STATUS_CHOICES)
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Amount must be a positive number.')
        return 



