from django.contrib import admin
from luckygardener.models import Author, ContestLuckyGardener
# Register your models here.

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name')
    list_filter = ('full_name', 'short_name')
    

@admin.register(ContestLuckyGardener)
class ContestLuckyGardenerAdmin(admin.ModelAdmin):
    list_display = ('comment',)

    def get_name(self, obj):
        return obj.author.full_name
    get_name.admin_order_field  = 'author__full_name'
    get_name.short_description = 'short_name'