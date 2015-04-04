# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0007_ballot_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='ballot',
            name='debug_only',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
