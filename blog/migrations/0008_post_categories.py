# Generated by Django 4.0 on 2023-10-14 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_post_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='categories',
            field=models.IntegerField(choices=[(0, 'Unspecified'), (1, 'Spirituality'), (2, 'Technology'), (3, 'Culture'), (4, 'Philosophy'), (5, 'Fun'), (6, 'Fiction')], default=0),
        ),
    ]
