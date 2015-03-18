# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='down_payment',
            field=models.DecimalField(verbose_name=b'Ether deposit', max_digits=100, decimal_places=2),
            preserve_default=True,
        ),
    ]
