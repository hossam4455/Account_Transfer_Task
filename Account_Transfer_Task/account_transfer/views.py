import csv
from django.shortcuts import render
from django.http import JsonResponse , HttpResponse
from .models import Account
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Account, Transaction
from .forms import TransactionForm
from django.db import transaction as db_transaction
from django.db.models import Q  # for complex queries
from decimal import Decimal, InvalidOperation
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Read and process the CSV file
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            for row in reader:
                if not row or row[0] == 'account_number':  # Skip empty rows or header rows
                    continue

                account_number = row[0]
                name = row[1]
                balance_str = row[2]  # Get the balance as a string

                # Skip rows where the balance is a non-numeric value like 'Balance' or other text
                if balance_str.lower() == 'balance':  # Check if the value is a header or invalid
                    continue
                
                try:
                    balance = Decimal(balance_str)  # Convert to Decimal to ensure it's a valid number
                except (ValueError, InvalidOperation):
                    return HttpResponse(f"Invalid balance value for account {account_number}. Problematic balance: {balance_str}", status=400)
                
                Account.objects.create(
                    account_number=account_number,
                    name=name,
                    balance=balance
                )
            return HttpResponse("CSV uploaded successfully!", status=200)
        except Exception as e:
            return HttpResponse(f"Error processing CSV: {e}", status=400)
    return render(request, 'upload_csv.html')

def make_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            from_account = form.cleaned_data['from_account']
            to_account = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']

            # Start a database transaction
            try:
                with db_transaction.atomic():
                    # Lock the rows for from_account and to_account
                    from_account = Account.objects.select_for_update().get(id=from_account.id)
                    to_account = Account.objects.select_for_update().get(id=to_account.id)

                    # Check if the from_account has enough balance
                    if from_account.balance >= amount:
                        # Perform the transaction
                        from_account.balance -= amount
                        to_account.balance += amount
                        from_account.save()
                        to_account.save()

                        # Create a transaction record
                        transaction = form.save(commit=False)
                        transaction.save()

                        # Redirect to the success page
                        return redirect('transaction_success')
                    else:
                        messages.error(request, "Insufficient balance in the from account.")
            except Account.DoesNotExist:
                messages.error(request, "Account(s) not found.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = TransactionForm()

    return render(request, 'make_transaction.html', {'form': form})
def transaction_success(request):
    return render(request, 'transaction_success.html')

def display_accounts(request):
    search_query = request.GET.get('search', '')  # Get the search query from the URL
    accounts = Account.objects.all()

    # If a search query is provided, filter accounts by account number or name
    if search_query:
        accounts = accounts.filter(
            Q(account_number__icontains=search_query) | 
            Q(name__icontains=search_query)
        )

    # Return the filtered accounts and search query to the template
    return render(request, 'display_accounts.html', {'accounts': accounts, 'search_query': search_query})
def home(request):
    return render(request, 'home.html')