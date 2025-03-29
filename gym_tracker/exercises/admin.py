from django.contrib import admin
from .models import Exercise, ExerciseCategory

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Información de Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'creator', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('difficulty', 'category', 'creator')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'difficulty')
        }),
        ('Detalles del Ejercicio', {
            'fields': ('primary_muscles', 'secondary_muscles', 'equipment', 'instructions', 'tips'),
            'classes': ('collapse',)
        }),
        ('Información de Auditoría', {
            'fields': ('creator', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
