# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0002_auto_20150317_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='down_payment',
            field=models.DecimalField(verbose_name=b'Ether deposit', max_digits=100, decimal_places=18),
            preserve_default=True,
        ),
    ]
