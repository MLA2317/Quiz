# Generated by Django 4.2.1 on 2023-05-22 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_result_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='categories',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='questions',
            new_name='question',
        ),
    ]