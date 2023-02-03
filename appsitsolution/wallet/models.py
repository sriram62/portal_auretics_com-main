from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from datetime import datetime

from .errors import InsufficientBalance

# We'll be using BigIntegerField by default instead
# of DecimalField for simplicity. This can be configured
# though by setting `WALLET_CURRENCY_STORE_FIELD` in your
# `settings.py`.
CURRENCY_STORE_FIELD = getattr(settings,
        'WALLET_CURRENCY_STORE_FIELD', models.BigIntegerField)


class Wallet(models.Model):
    # We should reference to the AUTH_USER_MODEL so that
    # when this module is used and a different User is used,
    # this would still work out of the box.
    #
    # See 'Referencing the User model' [1]
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="User")
    # This stores the wallet's current balance. Also acts
    # like a cache to the wallet's balance as well.
    # The date/time of the creation of this wallet.
    type = models.CharField(max_length=200, null=True, blank=True, verbose_name="Type")
    account = models.CharField(max_length=200, null=True, blank=True, verbose_name="Account")
    amount_in = models.DecimalField(default=0,decimal_places=2,max_digits=30, verbose_name="Amount out")
    amount_out = models.DecimalField(default=0, decimal_places=2,max_digits=30, verbose_name="Amount in")
    current_balance =  CURRENCY_STORE_FIELD(default=0.00,verbose_name="Balance")
    narration = models.CharField(max_length=200, null=True, blank=True, verbose_name="Narration")
    remarks = models.CharField(max_length=200, null=True, blank=True, verbose_name="Remarks")
    added_by_detail = models.TextField(verbose_name="Added by Details", null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    def deposit(self, value):
        """Deposits a value to the wallet.
        Also creates a new transaction with the deposit
        value.
        """
        self.transaction_set.create(
            value=value,
            running_balance=self.current_balance + value
        )
        self.current_balance += value
        self.save()

    def withdraw(self, value):
        """Withdraw's a value from the wallet.
        Also creates a new transaction with the withdraw
        value.
        Should the withdrawn amount is greater than the
        balance this wallet currently has, it raises an
        :mod:`InsufficientBalance` error. This exception
        inherits from :mod:`django.db.IntegrityError`. So
        that it automatically rolls-back during a
        transaction lifecycle.
        """
        if value > self.current_balance:
            raise InsufficientBalance('This wallet has insufficient balance.')

        self.transaction_set.create(
            value=-value,
            running_balance=self.current_balance - value
        )
        self.current_balance -= value
        self.save()

    def transfer(self, wallet, value):
        """Transfers an value to another wallet.
        Uses `deposit` and `withdraw` internally.
        """
        self.withdraw(value)
        wallet.deposit(value)

    def __str__(self):
        return f"{self.user.username}'s wallet "

class Transaction(models.Model):
    # The wallet that holds this transaction.
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    # The value of this transaction.
    value = CURRENCY_STORE_FIELD(default=0, verbose_name="Value")
    # The value of the wallet at the time of this
    # transaction. Useful for displaying transaction
    # history.
    running_balance = CURRENCY_STORE_FIELD(default=0, verbose_name="Running Balance")
    # The date/time of the creation of this transaction.
    created_at = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.wallet.user.username}'s wallet "

# Footnotes
# [1]: https://docs.djangoproject.com/en/1.9/topics/auth/customizing/#referencing-the-user-model


# class JuspayDipostedData(models.Model):
#     order_id = models.CharField(max_length=100, null=True,blank=True)
#     Signature = models.CharField(max_length=200, null=True,blank=True)
#     signature_algorithm = models.CharField(max_length=200, null=True,blank=True)


class JuspayDipostedData(models.Model):
    order_id = models.CharField(max_length=100, null=True,blank=True)
    Signature = models.CharField(max_length=200, null=True,blank=True)
    signature_algorithm = models.CharField(max_length=200, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.order_id
                    
