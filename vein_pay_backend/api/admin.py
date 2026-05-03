from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Wallet, BiometricData, Bill, Transaction


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Fields", {"fields": ("role",)}),
    )


class WalletAdmin(admin.ModelAdmin):
    list_display = ('owner', 'balance', 'updated_at')
    search_fields = ('owner__username',)


class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'initiating_shop', 'customer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'initiating_shop')
    search_fields = ('customer__username', 'initiating_shop__username')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_wallet', 'destination_wallet', 'amount', 'timestamp')
    search_fields = ('source_wallet__owner__username', 'destination_wallet__owner__username')


admin.site.register(Wallet, WalletAdmin)
admin.site.register(BiometricData)
admin.site.register(Bill, BillAdmin)
admin.site.register(Transaction, TransactionAdmin)