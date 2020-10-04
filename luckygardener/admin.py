from django.contrib import admin
from luckygardener.models import Author, ContestLuckyGardener
# Register your models here.

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(ContestLuckyGardener)
class ContestLuckyGardenerAdmin(admin.ModelAdmin):
    pass