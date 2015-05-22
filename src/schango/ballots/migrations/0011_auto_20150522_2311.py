# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0010_auto_20150506_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='ballot',
            name='is_complete',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ballot',
            name='num_revealers',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
