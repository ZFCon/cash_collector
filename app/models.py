from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Task(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_address = models.CharField(max_length=255)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due_at = models.DateTimeField()

    def __str__(self):
        return f"Task for {self.customer_name} - {self.amount_due} USD"


class CashCollector(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_collection_time = models.DateTimeField(null=True, blank=True)
    is_frozen = models.BooleanField(default=False)

    def update_frozen_status(self):
        if self.balance >= 5000:
            if (
                self.last_collection_time
                and timezone.now() >= self.last_collection_time + timedelta(days=2)
            ):
                self.is_frozen = True
        else:
            self.is_frozen = False
        self.save()

    def __str__(self):
        return self.user.username


class Collection(models.Model):
    cash_collector = models.ForeignKey(CashCollector, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    collected_at = models.DateTimeField(auto_now_add=True)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cash_collector.balance += self.amount_collected
        self.cash_collector.last_collection_time = timezone.now()
        self.cash_collector.update_frozen_status()


class Payment(models.Model):
    cash_collector = models.ForeignKey(CashCollector, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cash_collector.balance -= self.amount_paid
        self.cash_collector.update_frozen_status()
