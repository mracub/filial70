from django.contrib import admin
from cost_cadastr.models import Docs, CadastrCosts, FilesCost, Object
from cost_cadastr.models import ClObject, ClCadNumNum, ClExploitationChar, ClAssignationType, ClAssignationCode
from cost_cadastr.models import ClAssignationBuilding, ClObjectType, ClParenCadastralNumbers, ClElementConstr
from cost_cadastr.models import ClCadCost, ClKeyParam, ClKeyParamTypes, ClLocation
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

#ClAddress, ClCadNumNum, ClKeyParam, ClCadCost, ClElementConstr, ClObject, ClPeriod
@admin.register(ClLocation)
class ClLocationAdmin(admin.ModelAdmin):
    pass

@admin.register(ClCadNumNum)
class ClCadNumNumAdmin(admin.ModelAdmin):
    pass

@admin.register(ClKeyParam)
class ClKeyParamAdmin(admin.ModelAdmin):
    pass

@admin.register(ClCadCost)
class ClCadCostAdmin(admin.ModelAdmin):
    pass


@admin.register(ClObject)
class ClObjectAdmin(admin.ModelAdmin):
    pass

