# Generated by Django 3.2.16 on 2024-01-18 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_post_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='is_visible',
        ),
    ]
