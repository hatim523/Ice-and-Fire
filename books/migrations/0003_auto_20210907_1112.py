# Generated by Django 3.2.6 on 2021-09-07 06:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20210831_2226'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='author_obj',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='book',
            old_name='author_obj',
            new_name='name',
        ),
    ]
