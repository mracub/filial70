from django.contrib import admin
from ipd_xml_to_mif.models import RequestDoc, Contractor, RequestAppeal
# Register your models here.

@admin.register(RequestDoc)
class RequestDocAdmin(admin.ModelAdmin):
    pass

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    pass

@admin.register(RequestAppeal)
class RequestAppealAdmin(admin.ModelAdmin):
    pass