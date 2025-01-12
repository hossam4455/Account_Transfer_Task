import pytest
from django.urls import reverse
from django.test import Client
from account_transfer.models import Account
from decimal import Decimal

@pytest.mark.django_db
def test_make_transaction_valid():
    client = Client()

    # Set up test data
    from_account = Account.objects.create(account_number="12345", name="John Doe2", balance=1000)
    to_account = Account.objects.create(account_number="67890", name="Jane Doe1", balance=500)

    form_data = {
        'from_account': from_account.id,
        'to_account': to_account.id,
        'amount': 100,
    }

    response = client.post(reverse('make_transaction'), data=form_data)

    from_account.refresh_from_db()
    to_account.refresh_from_db()

    assert from_account.balance == Decimal('900.00')
    assert to_account.balance == Decimal('600.00')
    assert response.status_code == 302  # Check for success redirect
