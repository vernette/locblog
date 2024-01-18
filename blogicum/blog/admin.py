from django.contrib import admin

from .models import Category, Comment, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    list_filter = ['is_published']


class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['is_published']


class PostAdmin(admin.ModelAdmin):
    search_fields = ['title', 'text']
    list_filter = ['is_published']


class CommentAdmin(admin.ModelAdmin):
    search_fields = ['text', 'author']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
