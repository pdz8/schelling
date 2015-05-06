# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0009_auto_20150429_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='redeem_time',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ballot',
            name='reveal_time',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ballot',
            name='start_time',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
    ]
