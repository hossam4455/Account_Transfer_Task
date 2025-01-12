from django.contrib import admin
from .models import Account, Transaction


@admin.register(Transaction)  # Automatically registers the model
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('from_account', 'to_account', 'amount', 'timestamp')
