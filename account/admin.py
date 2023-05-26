from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account
from .forms import AccountChangeForm


# @admin.register(Account)
# class AccountAdmin(admin.ModelAdmin):
#     list_display = ['id', 'username', 'avatar', 'bio', 'created_date']


class AccountAdmin(UserAdmin):
    form = AccountChangeForm
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2',)}),
    )
    list_display = ('id', 'username', 'image_tag', 'is_superuser',
                    'is_staff', 'is_active', 'modified_date', 'created_date')
    ordering = None
    readonly_fields = ('modified_date', 'created_date')
    list_filter = ('created_date', 'is_superuser', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'avatar', 'bio', 'password')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('modified_date', 'created_date')}),
    )
    search_fields = ('username',)


admin.site.register(Account, AccountAdmin)