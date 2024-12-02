# Generated by Django 5.1.3 on 2024-11-30 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('vendor', models.CharField(max_length=100)),
                ('trans', models.CharField(max_length=100)),
                ('cc', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('exp', models.CharField(max_length=7)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('brand', models.CharField(max_length=50)),
                ('authorization', models.CharField(max_length=100)),
                ('timeStamp', models.BigIntegerField()),
            ],
        ),
    ]
