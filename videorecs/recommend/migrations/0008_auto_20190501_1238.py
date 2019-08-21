# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-05-01 12:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0007_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalizeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=64)),
                ('model_arn', models.CharField(max_length=256)),
                ('model_type', models.CharField(choices=[('recommend', 'Recommendations'), ('ranking', 'List Re-Ranking'), ('sims', 'Similar Items')], default='recommend', max_length=10)),
            ],
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
