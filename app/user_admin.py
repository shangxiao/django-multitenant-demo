import django.contrib.auth.admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import TenantUser


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "is_staff")
    list_filter = ("is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = []


class TenantUserCreationForm(UserCreationForm):
    class Meta:
        model = TenantUser
        fields = ("tenant", "email")


class TenantUserChangeForm(UserChangeForm):
    class Meta:
        model = TenantUser
        fields = "__all__"


class TenantUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("tenant", "email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("tenant", "email", "password1", "password2"),
            },
        ),
    )
    form = TenantUserChangeForm
    add_form = TenantUserCreationForm
