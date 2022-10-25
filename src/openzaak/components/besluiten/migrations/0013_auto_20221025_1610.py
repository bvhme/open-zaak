# Generated by Django 3.2.15 on 2022-10-25 16:10

from django.db import migrations, models
import django.db.models.deletion
import openzaak.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("zgw_consumers", "0016_auto_20220818_1412"),
        ("besluiten", "0012_auto_20220818_1617"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="besluitinformatieobject",
            name="unique_besluit_and_external_document",
        ),
        migrations.AlterField(
            model_name="besluit",
            name="_besluittype_base_url",
            field=models.ForeignKey(
                blank=True,
                help_text="Basisdeel van URL-referentie naar het extern BESLUITTYPE (in een andere Catalogi API).",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="zgw_consumers.service",
            ),
        ),
        migrations.AlterField(
            model_name="besluit",
            name="_besluittype_relative_url",
            field=openzaak.utils.fields.RelativeURLField(
                blank=True,
                help_text="Relatief deel van URL-referentie naar het extern BESLUITTYPE (in een andere Catalogi API).",
                max_length=1000,
                null=True,
                verbose_name="besluittype relative url",
            ),
        ),
        migrations.AlterField(
            model_name="besluit",
            name="_zaak_base_url",
            field=models.ForeignKey(
                blank=True,
                help_text="Basis deel van URL-referentie naar de externe ZAAK (in een andere Zaken API).",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="zgw_consumers.service",
            ),
        ),
        migrations.AlterField(
            model_name="besluit",
            name="_zaak_relative_url",
            field=openzaak.utils.fields.RelativeURLField(
                blank=True,
                help_text="Relatief deel van URL-referentie naar de externe ZAAK (in een andere Zaken API).",
                max_length=1000,
                null=True,
                verbose_name="zaak relative url",
            ),
        ),
        migrations.AlterField(
            model_name="besluitinformatieobject",
            name="_informatieobject_relative_url",
            field=openzaak.utils.fields.RelativeURLField(
                blank=True,
                help_text="Relatief deel van URL-referentie naar de externe API",
                max_length=1000,
                null=True,
                verbose_name="informatieobject relative url",
            ),
        ),
        migrations.AddConstraint(
            model_name="besluitinformatieobject",
            constraint=models.UniqueConstraint(
                condition=models.Q(("_informatieobject_relative_url__isnull", False)),
                fields=(
                    "besluit",
                    "_informatieobject_base_url",
                    "_informatieobject_relative_url",
                ),
                name="unique_besluit_and_external_document",
            ),
        ),
    ]
