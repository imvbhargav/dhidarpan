# Generated by Django 4.1.4 on 2022-12-21 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_rename_display_pictute_profileinfo_display_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profileinfo',
            name='display_picture',
            field=models.ImageField(default='profiles/NULL.png', upload_to='profiles'),
        ),
    ]