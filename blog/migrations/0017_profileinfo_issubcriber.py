# Generated by Django 4.0 on 2023-12-09 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_profileinfo_isgoogleuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileinfo',
            name='isSubcriber',
            field=models.BooleanField(default=False),
        ),
    ]
