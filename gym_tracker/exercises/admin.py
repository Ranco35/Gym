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
    list_display = ('name', 'muscle_group', 'difficulty', 'created_by', 'created_at')
    search_fields = ('name', 'description', 'primary_muscles')
    list_filter = ('difficulty', 'muscle_group', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'muscle_group', 'difficulty')
        }),
        ('Detalles del Ejercicio', {
            'fields': ('primary_muscles', 'secondary_muscles', 'equipment', 'tips'),
            'classes': ('collapse',)
        }),
        ('Multimedia', {
            'fields': ('image', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Información de Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
