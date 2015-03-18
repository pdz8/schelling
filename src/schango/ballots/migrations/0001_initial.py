# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=42)),
                ('question', models.CharField(max_length=160)),
                ('start_time', models.DateTimeField()),
                ('reveal_time', models.DateTimeField()),
                ('redeem_time', models.DateTimeField()),
                ('down_payment', models.DecimalField(max_digits=100, decimal_places=2)),
                ('max_choice', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
