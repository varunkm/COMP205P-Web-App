# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-11 12:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bonds', '0006_auto_20170304_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('syndicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonds.Syndicate')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonds.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ProductInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('interest_rate', models.DecimalField(decimal_places=5, max_digits=6)),
                ('min_deposit', models.IntegerField()),
                ('payout_period', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('kind', models.TextField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonds.Account')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonds.ProductInfo'),
        ),
        migrations.AddField(
            model_name='account',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonds.UserProfile'),
        ),
    ]