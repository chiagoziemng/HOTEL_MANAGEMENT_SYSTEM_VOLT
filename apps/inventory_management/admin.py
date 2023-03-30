from django.contrib import admin
from .models import  *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class DrinkResource(resources.ModelResource): 
    class Meta: 
        model = Drink 
    
class DrinkAdmin(ImportExportModelAdmin): 
    resource_class = DrinkResource


class SaleResource(resources.ModelResource): 
    class Meta: 
        model = Sale 
    
class SaleAdmin(ImportExportModelAdmin): 
    resource_class = SaleResource


class DebtResource(resources.ModelResource): 
    class Meta: 
        model = Debt
    
class DebtAdmin(ImportExportModelAdmin): 
    resource_class = DebtResource


class ComplimentaryResource(resources.ModelResource): 
    class Meta: 
        model = Complimentary
    
class ComplimentaryAdmin(ImportExportModelAdmin): 
    resource_class = ComplimentaryResource


admin.site.register(Drink, DrinkAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Debt, DebtAdmin)
admin.site.register(Complimentary, ComplimentaryAdmin)
