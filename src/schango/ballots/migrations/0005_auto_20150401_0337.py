# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0004_ethaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='address',
            field=models.CharField(max_length=40),
            preserve_default=True,
        ),
    ]
