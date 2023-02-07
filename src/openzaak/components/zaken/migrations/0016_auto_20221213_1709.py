# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2022 Dimpact
# Generated by Django 3.2.16 on 2022-12-13 17:09

from django.db import migrations, models

import vng_api_common.fields


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0015_auto_20221116_1437"),
    ]

    operations = [
        migrations.CreateModel(
            name="ZaakIdentificatie",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identificatie",
                    models.CharField(
                        db_index=True,
                        help_text="Unique identification (within an organisation). Open Zaak generates this number uniquely even across organisation identifiers.",
                        max_length=40,
                        verbose_name="value",
                    ),
                ),
                ("bronorganisatie", vng_api_common.fields.RSINField(max_length=9)),
            ],
            options={
                "verbose_name": "zaak identification",
                "verbose_name_plural": "zaak identifications",
            },
        ),
        migrations.AddConstraint(
            model_name="zaakidentificatie",
            constraint=models.UniqueConstraint(
                fields=("identificatie", "bronorganisatie"),
                name="unique_bronorganisation_identification",
            ),
        ),
    ]