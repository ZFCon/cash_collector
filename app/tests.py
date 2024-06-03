from django.test import TestCase
from django.contrib.auth.models import User
from .models import CashCollector, Task, Collection, Payment
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

class CashCollectorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', password='password')
        self.collector = CashCollector.objects.create(user=self.user)
        self.task1 = Task.objects.create(customer_name='Customer 1', customer_address='Address 1', amount_due=1000, amount_due_at=timezone.now())
        self.task2 = Task.objects.create(customer_name='Customer 2', customer_address='Address 2', amount_due=6000, amount_due_at=timezone.now() + timedelta(hours=1))
        self.client = APIClient()
        self.client.login(username='john', password='password')

    def test_collect_cash(self):
        response = self.client.post('/api/collect/', {'cash_collector': self.collector.id, 'task': self.task1.id, 'amount_collected': 1000})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.collector.refresh_from_db()
        self.assertEqual(self.collector.balance, 1000)

    def test_frozen_status(self):
        Collection.objects.create(cash_collector=self.collector, task=self.task1, amount_collected=1000)
        Collection.objects.create(cash_collector=self.collector, task=self.task2, amount_collected=6000)
        self.collector.last_collection_time = timezone.now() - timedelta(days=2)
        self.collector.update_frozen_status()
        self.collector.refresh_from_db()
        self.assertTrue(self.collector.is_frozen)

    def test_pay_manager(self):
        Collection.objects.create(cash_collector=self.collector, task=self.task1, amount_collected=1000)
        response = self.client.post('/api/pay/', {'cash_collector': self.collector.id, 'amount_paid': 500})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.collector.refresh_from_db()
        self.assertEqual(self.collector.balance, 500)
