from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text')
    list_filter = ('is_published',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('text', 'author')
