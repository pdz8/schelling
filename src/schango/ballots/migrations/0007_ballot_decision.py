# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0006_auto_20150404_0225'),
    ]

    operations = [
        migrations.AddField(
            model_name='ballot',
            name='decision',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
