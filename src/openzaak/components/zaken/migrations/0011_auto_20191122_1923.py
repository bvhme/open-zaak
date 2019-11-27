# Generated by Django 2.2.4 on 2019-11-22 18:23

from django.db import migrations, models
import openzaak.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0010_auto_20191122_1411"),
    ]

    operations = [
        migrations.AddField(
            model_name="klantcontact",
            name="onderwerp",
            field=models.CharField(
                blank=True,
                help_text="Het onderwerp waarover contact is geweest met de klant.",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="klantcontact",
            name="toelichting",
            field=models.CharField(
                blank=True,
                help_text="Een toelichting die inhoudelijk het contact met de klant beschrijft.",
                max_length=1000,
            ),
        ),
        migrations.AlterField(
            model_name="zaak",
            name="verlenging_duur",
            field=openzaak.utils.fields.DurationField(
                blank=True,
                help_text="Het aantal werkbare dagen waarmee de doorlooptijd van de behandeling van de ZAAK is verlengd (of verkort) ten opzichte van de eerder gecommuniceerde doorlooptijd.",
                null=True,
                verbose_name="duur verlenging",
            ),
        ),
    ]
