import pytest
from django.urls import reverse
from django.test import Client
from account_transfer.models import Account
from decimal import Decimal

@pytest.mark.django_db
def test_make_transaction_valid():
    client = Client()

    # Create two accounts with unique account numbers
    from_account = Account.objects.create(account_number="12345", name="John Doe", balance=1000)
    to_account = Account.objects.create(account_number="67890", name="Jane Doe", balance=500)

    # Create a valid transaction form
    form_data = {
        'from_account': from_account.id,
        'to_account': to_account.id,
        'amount': 100,
    }

    # Send a POST request with valid data
    response = client.post(reverse('make_transaction'), data=form_data)

    # Check that the transaction was successful and the accounts' balances were updated
    from_account.refresh_from_db()
    to_account.refresh_from_db()
    
    assert from_account.balance == Decimal('900.00')  # Balance should decrease
    assert to_account.balance == Decimal('600.00')  # Balance should increase
    assert response.status_code == 302  # Redirect to success page

# Ensure pytest is properly imported and configured.
