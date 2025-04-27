from django.contrib import admin
from .models import TrainerProfile, TrainerStudent, LiveTrainingSession, LiveSet, TrainerFeedback, TrainerTraining, TrainerSet, TrainerTrainingDay

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'max_students', 'active')
    list_filter = ('active', 'specialization')
    search_fields = ('user__username', 'user__email', 'specialization')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TrainerStudent)
class TrainerStudentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'student', 'active', 'start_date')
    list_filter = ('active', 'start_date')
    search_fields = ('trainer__username', 'student__username', 'notes')
    readonly_fields = ('start_date', 'created_at', 'updated_at')

@admin.register(LiveTrainingSession)
class LiveTrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('training', 'trainer_student', 'status', 'started_at', 'ended_at')
    list_filter = ('status', 'started_at')
    search_fields = ('trainer_student__trainer__username', 'trainer_student__student__username')
    readonly_fields = ('started_at',)

@admin.register(LiveSet)
class LiveSetAdmin(admin.ModelAdmin):
    list_display = ('session', 'set', 'completed_by', 'weight', 'reps', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('session__trainer_student__trainer__username', 'session__trainer_student__student__username')
    readonly_fields = ('completed_at',)

@admin.register(TrainerFeedback)
class TrainerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('trainer_student', 'training', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('trainer_student__trainer__username', 'trainer_student__student__username')
    readonly_fields = ('created_at',)

class TrainerSetInline(admin.TabularInline):
    model = TrainerSet
    extra = 0

# Definimos primero TrainerTrainingDayInline
class TrainerTrainingDayInline(admin.TabularInline):
    model = TrainerTrainingDay
    extra = 0

@admin.register(TrainerTraining)
class TrainerTrainingAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_by', 'start_date', 'completed', 'created_at')
    list_filter = ('completed', 'start_date', 'created_at')
    search_fields = ('name', 'user__username', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TrainerTrainingDayInline]

@admin.register(TrainerSet)
class TrainerSetAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'training_day', 'sets_count', 'reps', 'weight', 'order')
    list_filter = ('created_at',)
    search_fields = ('exercise', 'training_day__training__name', 'training_day__training__user__username')
    ordering = ('training_day', 'order')

@admin.register(TrainerTrainingDay)
class TrainerTrainingDayAdmin(admin.ModelAdmin):
    list_display = ('training', 'day_of_week', 'focus')
    list_filter = ('day_of_week',)
    search_fields = ('training__name', 'training__user__username', 'focus')
    inlines = [TrainerSetInline]
