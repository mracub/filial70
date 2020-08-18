from django.contrib import admin
from cost_cadastr.models import Docs, CadastrCosts, FilesCost, Object, XmlDocEgrn
# Register your models here.


@admin.register(Docs)
class DocsAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = 'Docs'
        verbose_name_plural = 'Docs'

@admin.register(CadastrCosts)
class CadastrCostsAdmin(admin.ModelAdmin):
    pass

@admin.register(FilesCost)
class FilesCostAdmin(admin.ModelAdmin):
    pass

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    pass

@admin.register(XmlDocEgrn)
class XmlDocEgrnAdmin(admin.ModelAdmin):
    pass
