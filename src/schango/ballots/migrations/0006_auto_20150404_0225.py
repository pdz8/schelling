# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0005_auto_20150401_0337'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ballot',
            old_name='max_choice',
            new_name='max_option',
        ),
    ]
