# Generated by Django 4.0.3 on 2023-09-12 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0004_inputlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goldprice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.TextField(blank=True, null=True)),
                ('sell', models.FloatField(blank=True, null=True)),
                ('buy', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'goldprice',
                'managed': False,
            },
        ),
    ]
