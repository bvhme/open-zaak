# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2022 Dimpact
# Generated by Django 3.2.16 on 2022-12-14 08:24

import django.db.models.deletion
from django.db import migrations, models
from django.db.models.signals import post_save

from vng_api_common.caching.signals import mark_related_instances_for_etag_update

from openzaak.utils.migrations import temp_disconnect_signal


def forwards(apps, schema_editor):
    Zaak = apps.get_model("zaken", "Zaak")
    ZaakIdentificatie = apps.get_model("zaken", "ZaakIdentificatie")
    # lock zaken table for writing, reads are still possible
    schema_editor.execute(f"LOCK TABLE {Zaak._meta.db_table} IN EXCLUSIVE MODE")

    with temp_disconnect_signal(
        post_save, mark_related_instances_for_etag_update, sender=None
    ):
        # copy over all the existing data of Zaak model to ZaakIdentificatie model
        for zaak in Zaak.objects.all().iterator():
            zaak_identification = ZaakIdentificatie.objects.create(
                id=zaak.id,
                bronorganisatie=zaak.bronorganisatie,
                identificatie=zaak.identificatie,
            )
            zaak.identificatie_ptr = zaak_identification
            zaak.save(update_fields=["identificatie_ptr"])

    # synchronize the sequences so that zaak.id and zaakidentificatie.id are lined up
    # The next migrate sets the models up for multi-table inheritance, and the existing
    # IDs should be properly transferred
    max_zaak_id = Zaak.objects.aggregate(max_id=models.Max("id"))["max_id"]
    if max_zaak_id is None:
        return

    for model in (Zaak, ZaakIdentificatie):
        schema_editor.execute(
            f"select setval('{model._meta.db_table}_id_seq', {max_zaak_id})"
        )


def backwards(apps, schema_editor):
    Zaak = apps.get_model("zaken", "Zaak")
    # lock zaken table for writing, reads are still possible
    schema_editor.execute(f"LOCK TABLE {Zaak._meta.db_table} IN EXCLUSIVE MODE")

    with temp_disconnect_signal(
        post_save, mark_related_instances_for_etag_update, sender=None
    ):
        # copy over all the existing data of Zaak model to ZaakIdentificatie model
        for zaak in Zaak.objects.select_related("identificatie_ptr").iterator():
            zaak.identificatie = zaak.identificatie_ptr.identificatie
            zaak.bronorganisatie = zaak.identificatie_ptr.bronorganisatie
            zaak.save(update_fields=["identificatie", "bronorganisatie"])


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0016_auto_20221213_1709"),
    ]

    operations = [
        migrations.AddField(
            model_name="zaak",
            name="identificatie_ptr",
            field=models.OneToOneField(
                help_text="Zaak identification details are tracked in a separate table so numbers can be generated/reserved before the zaak is actually created.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="zaken.zaakidentificatie",
                verbose_name="Zaak identification details",
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]