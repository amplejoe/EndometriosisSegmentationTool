# Generated by Django 3.2.3 on 2021-05-27 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20210524_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]