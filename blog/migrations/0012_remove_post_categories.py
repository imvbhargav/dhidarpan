# Generated by Django 4.0 on 2023-10-14 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_category_alter_post_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='categories',
        ),
    ]
