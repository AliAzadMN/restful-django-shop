# Generated by Django 5.0.1 on 2024-01-29 20:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='status',
        ),
    ]
