from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Main information', {
            'fields': [
                'email', 'currency', 'balance', 'first_name', 'last_name',
                'born_city', 'born_date'
            ]
        })
    ]
    list_display = (
        'email', 'currency', 'balance', 'created_at', 'first_name', 'last_name'
    )


admin.site.register(User, UserAdmin)
