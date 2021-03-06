# Generated by Django 3.0.2 on 2020-01-31 08:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('txn_id', models.CharField(max_length=20, verbose_name='Transaction ID')),
                ('description', models.CharField(max_length=145, verbose_name='Description')),
                ('txn_type', models.IntegerField(choices=[(0, 'Debit'), (1, 'Credit')])),
                ('status', models.CharField(max_length=10, verbose_name='Status')),
                ('currency', models.CharField(default='INR', max_length=5, verbose_name='Currency')),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]
