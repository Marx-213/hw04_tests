# Generated by Django 2.2.16 on 2022-05-18 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20220518_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
