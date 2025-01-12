from django.urls import path
from . import views

urlpatterns = [
       path('', views.home, name='home'),
      path('upload_csv/', views.upload_csv, name='upload_csv'),
       path('transaction/', views.make_transaction, name='make_transaction'),
       path('transaction/success/', views.transaction_success, name='transaction_success'),
        path('accounts/', views.display_accounts, name='display_accounts'),
]
