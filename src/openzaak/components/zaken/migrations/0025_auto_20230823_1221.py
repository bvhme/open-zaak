# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2023 Dimpact
# Generated by Django 3.2.18 on 2023-08-23 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0024_alter_status_datum_status_gezet"),
    ]

    operations = [
        migrations.AddField(
            model_name="zaak",
            name="processobject_datumkenmerk",
            field=models.CharField(
                blank=True,
                help_text="De naam van de attribuutsoort van het procesobject dat bepalend is voor het einde van de procestermijn.",
                max_length=250,
                verbose_name="datumkenmerk",
            ),
        ),
        migrations.AddField(
            model_name="zaak",
            name="processobject_identificatie",
            field=models.CharField(
                blank=True,
                help_text="De unieke aanduiding van het procesobject.",
                max_length=250,
                verbose_name="identificatie",
            ),
        ),
        migrations.AddField(
            model_name="zaak",
            name="processobject_objecttype",
            field=models.CharField(
                blank=True,
                help_text="Het soort object dat het procesobject representeert.",
                max_length=250,
                verbose_name="objecttype",
            ),
        ),
        migrations.AddField(
            model_name="zaak",
            name="processobject_registratie",
            field=models.CharField(
                blank=True,
                help_text="De naam van de registratie waarvan het procesobject deel uit maakt.",
                max_length=250,
                verbose_name="registratie",
            ),
        ),
        migrations.AddField(
            model_name="zaak",
            name="processobjectaard",
            field=models.CharField(
                blank=True,
                help_text="Omschrijving van het object, subject of gebeurtenis waarop, vanuit archiveringsoptiek, de zaak betrekking heeft.",
                max_length=200,
                verbose_name="procesobjectaard",
            ),
        ),
        migrations.AddField(
            model_name="zaak",
            name="resultaattoelichting",
            field=models.TextField(
                blank=True,
                help_text="Een toelichting op wat het resultaat van de zaak inhoudt.",
                max_length=1000,
                verbose_name="resultaattoelichting",
            ),
        ),
        migrations.AddField(
            model_name="zaak",
            name="startdatum_bewaartermijn",
            field=models.DateField(
                blank=True,
                help_text="De datum die de start markeert van de termijn waarop het zaakdossier vernietigd moet worden.",
                null=True,
                verbose_name="startdatum bewaartermijn",
            ),
        ),
    ]
