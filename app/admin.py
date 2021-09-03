from django.contrib import admin

from .models import (
    AdminUser,
    ContractorUser,
    Level,
    Site,
    Tenant,
    TenantUser,
    Vendor,
    VendorUser,
)
from .user_admin import TenantUserAdmin, UserAdmin

admin.site.register(Level)
admin.site.register(Site)
admin.site.register(Tenant)
admin.site.register(Vendor)


admin.register(AdminUser, ContractorUser, VendorUser)(UserAdmin)
admin.register(TenantUser)(TenantUserAdmin)
