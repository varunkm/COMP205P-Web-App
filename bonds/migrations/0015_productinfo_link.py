# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-07 13:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonds', '0014_auto_20170406_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinfo',
            name='link',
            field=models.CharField(default='', max_length=140),
        ),
    ]