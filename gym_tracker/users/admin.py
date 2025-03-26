from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, TrainerUser

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('avatar_tag', 'username', 'email', 'role_badge', 'is_active', 'last_login', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': (('username', 'email'), ('first_name', 'last_name'), 'role'),
            'classes': ('wide',)
        }),
        ('Permisos', {
            'fields': (('is_active', 'is_staff', 'is_superuser'), 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Medidas Corporales', {
            'fields': (
                ('peso', 'altura'),
                ('cuello', 'pecho', 'cintura'),
                ('cadera', 'brazos', 'muslo'),
                'muñeca'
            ),
            'classes': ('wide',)
        }),
        ('Fechas', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )

    def avatar_tag(self, obj):
        return format_html('<img src="/static/admin/img/user.png" style="width: 30px; height: 30px; border-radius: 50%;" />')
    avatar_tag.short_description = ''

    def role_badge(self, obj):
        colors = {
            'ADMIN': 'red',
            'TRAINER': 'blue',
            'USER': 'green'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.role, 'gray'),
            obj.get_role_display()
        )
    role_badge.short_description = 'Rol'

@admin.register(TrainerUser)
class TrainerUserAdmin(admin.ModelAdmin):
    list_display = ('trainer_name', 'user_name', 'fecha_inicio', 'activo', 'status_badge')
    list_filter = ('activo', 'fecha_inicio')
    search_fields = ('trainer__username', 'user__username')
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Relación', {
            'fields': (('trainer', 'user'), 'activo', 'fecha_inicio')
        }),
        ('Detalles', {
            'fields': ('notas',)
        }),
    )

    def trainer_name(self, obj):
        return obj.trainer.get_full_name() or obj.trainer.username
    trainer_name.short_description = 'Entrenador'

    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'Usuario'

    def status_badge(self, obj):
        if obj.activo:
            color = 'green'
            text = 'Activo'
        else:
            color = 'red'
            text = 'Inactivo'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    status_badge.short_description = 'Estado' 