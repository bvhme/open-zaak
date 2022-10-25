# Generated by Django 3.2.15 on 2022-10-25 16:13

from django.db import migrations
import openzaak.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("documenten", "0021_auto_20220906_1546"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="_informatieobjecttype_relative_url",
            field=openzaak.utils.fields.RelativeURLField(
                blank=True,
                help_text="Relatief deel van URL-referentie naar extern INFORMATIEOBJECTTYPE (in een andere Catalogi API).",
                max_length=1000,
                null=True,
                verbose_name="informatieobjecttype relative url",
            ),
        ),
        migrations.AlterField(
            model_name="objectinformatieobject",
            name="_object_relative_url",
            field=openzaak.utils.fields.RelativeURLField(
                blank=True,
                help_text="Relatief deel van URL-referentie naar extern API.",
                max_length=1000,
                null=True,
                verbose_name="besluit relative url",
            ),
        ),
    ]
