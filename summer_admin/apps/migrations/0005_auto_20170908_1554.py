# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-08 07:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_auto_20170908_1551'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agent_charge',
            options={'managed': True, 'verbose_name': '代理充值表表', 'verbose_name_plural': '代理充值'},
        ),
        migrations.AlterModelTable(
            name='agent_charge',
            table='agent_charge',
        ),
    ]
