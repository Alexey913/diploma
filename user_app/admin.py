from django.contrib import admin

from .models import User, Data

@admin.action(description="Преобразовать номер телефона")
def change_phone_format(modeladmin, request, queryset):
    for item in queryset:
        if item.phone and not str(item.phone).startswith('7'):
            item.phone = int('7' + str(item.phone)[1:])
            item.save()

class UserAdmin(admin.ModelAdmin):
    """Список пользователей"""
    list_display = ['email', 'phone', 'hash_password']
    ordering = ['email', 'phone']
    list_filter = ['email', 'phone']
    search_fields = ['phone']
    search_help_text = 'Поиск по полю Телефон (phone)'
    actions = [change_phone_format]

    """Отедельный пользователь"""
    fields = ['id', 'email', 'phone', 'hash_password', 'salt']
    readonly_fields = ['id', 'hash_password', 'salt']

    fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': ['id'],
            },
        ),
        (
            'Контакты',
            {
                'classes': ['collapse'],
                'description': 'Телефон и e-mail пользователя',
                'fields': ['phone', 'email'],
            },
        ),
        (
            'Безопасность',
            {
                'description': 'Информация о пароле',
                'fields': ['hash_password', 'salt'],
            },
        ),
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Data)
