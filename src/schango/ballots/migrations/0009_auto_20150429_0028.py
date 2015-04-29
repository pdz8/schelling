# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0008_ballot_debug_only'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='down_payment',
            field=models.CharField(max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ballot',
            name='question',
            field=models.CharField(max_length=256),
            preserve_default=True,
        ),
    ]
