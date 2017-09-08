# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-15 05:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account', models.CharField(default='', max_length=255)),
                ('ali_id', models.CharField(default='', max_length=255)),
                ('cash', models.FloatField()),
                ('gold', models.FloatField()),
                ('money', models.FloatField()),
                ('rebate', models.FloatField()),
                ('email', models.CharField(default='', max_length=2000)),
                ('father_id', models.CharField(default='', max_length=255)),
                ('image', models.CharField(default='', max_length=4000)),
                ('ip_config', models.CharField(default='', max_length=255)),
                ('open_id', models.CharField(default='', max_length=255)),
                ('password', models.CharField(default='', max_length=255)),
                ('username', models.CharField(default='', max_length=4000)),
                ('uuid', models.CharField(default='', max_length=255)),
                ('last_login_date', models.DateTimeField()),
                ('regist_date', models.DateTimeField()),
                ('referee', models.IntegerField(default=0)),
                ('sex', models.IntegerField(default=0)),
                ('vip', models.IntegerField(default=0)),
                ('user_info', models.TextField(default='')),
            ],
            options={
                'verbose_name': '用户表',
                'db_table': 'users',
                'verbose_name_plural': '用户',
                'managed': False,
            },
        ),
    ]
