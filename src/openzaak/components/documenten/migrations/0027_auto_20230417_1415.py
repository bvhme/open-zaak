# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2022 Dimpact
# Generated by Django 3.2.18 on 2023-04-17 14:15

from django.db import migrations


def populate_private_voltooid_attribute(apps, schema_editor):
    BestandsDeel = apps.get_model("documenten", "BestandsDeel")

    for bestandsdeel in BestandsDeel.objects.all():
        bestandsdeel._voltooid = bestandsdeel.inhoud.size == bestandsdeel.omvang
        bestandsdeel.save()


class Migration(migrations.Migration):

    dependencies = [
        ("documenten", "0026_bestandsdeel__voltooid"),
    ]

    operations = [
        migrations.RunPython(
            populate_private_voltooid_attribute, migrations.RunPython.noop
        ),
    ]
