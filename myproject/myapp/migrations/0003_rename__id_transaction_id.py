# Generated by Django 5.1.3 on 2024-11-30 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_transaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='_id',
            new_name='id',
        ),
    ]
