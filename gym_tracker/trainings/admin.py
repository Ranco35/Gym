from django.contrib import admin
from .models import Training, Set, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'birth_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('created_at', 'birth_date')
    raw_id_fields = ('user',)

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['exercise', 'user', 'date', 'completed', 'total_sets', 'reps', 'weight']
    list_filter = ['completed', 'date', 'user']
    search_fields = ['exercise__name', 'user__username', 'notes']
    raw_id_fields = ['user', 'exercise']
    date_hierarchy = 'date'

@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['training', 'set_number', 'weight', 'reps', 'completed']
    list_filter = ['completed', 'training__date']
    search_fields = ['training__exercise__name']
    raw_id_fields = ['user', 'training', 'exercise']
