# Generated by Django 3.0.2 on 2020-02-01 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_auto_20200131_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='txn_id',
            field=models.CharField(max_length=20, unique=True, verbose_name='Transaction ID'),
        ),
    ]