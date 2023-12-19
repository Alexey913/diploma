from django.contrib import admin

from .models import User, Data


admin.site.register(User)
admin.site.register(Data)


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'hash_password']
