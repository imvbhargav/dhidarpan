# Generated by Django 4.1.4 on 2023-11-19 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_profileinfo_follows'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=200, null=True)),
            ],
        ),
    ]