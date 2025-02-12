# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2022 Dimpact
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_filters import filters
from django_loose_fk.filters import FkOrUrlFieldFilter
from django_loose_fk.utils import get_resource_for_path
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_field_attribute, get_help_text

from openzaak.utils.filters import MaximaleVertrouwelijkheidaanduidingFilter

from ..models import (
    KlantContact,
    Resultaat,
    Rol,
    Status,
    Zaak,
    ZaakContactMoment,
    ZaakInformatieObject,
    ZaakObject,
    ZaakVerzoek,
)


class ZaakFilter(FilterSet):
    maximale_vertrouwelijkheidaanduiding = MaximaleVertrouwelijkheidaanduidingFilter(
        field_name="vertrouwelijkheidaanduiding",
        help_text=(
            "Zaken met een vertrouwelijkheidaanduiding die beperkter is dan de "
            "aangegeven aanduiding worden uit de resultaten gefiltered."
        ),
    )

    rol__betrokkene_identificatie__natuurlijk_persoon__inp_bsn = filters.CharFilter(
        field_name="rol__natuurlijkpersoon__inp_bsn",
        help_text=get_help_text("zaken.NatuurlijkPersoon", "inp_bsn"),
        max_length=get_field_attribute(
            "zaken.NatuurlijkPersoon", "inp_bsn", "max_length"
        ),
    )
    rol__betrokkene_identificatie__natuurlijk_persoon__anp_identificatie = filters.CharFilter(
        field_name="rol__natuurlijkpersoon__anp_identificatie",
        help_text=get_help_text("zaken.NatuurlijkPersoon", "anp_identificatie"),
        max_length=get_field_attribute(
            "zaken.NatuurlijkPersoon", "anp_identificatie", "max_length"
        ),
    )
    rol__betrokkene_identificatie__natuurlijk_persoon__inp_a_nummer = filters.CharFilter(
        field_name="rol__natuurlijkpersoon__inp_a_nummer",
        help_text=get_help_text("zaken.NatuurlijkPersoon", "inp_a_nummer"),
        max_length=get_field_attribute(
            "zaken.NatuurlijkPersoon", "inp_a_nummer", "max_length"
        ),
    )
    rol__betrokkene_identificatie__niet_natuurlijk_persoon__inn_nnp_id = filters.CharFilter(
        field_name="rol__nietnatuurlijkpersoon__inn_nnp_id",
        help_text=get_help_text("zaken.NietNatuurlijkPersoon", "inn_nnp_id"),
    )
    rol__betrokkene_identificatie__niet_natuurlijk_persoon__ann_identificatie = filters.CharFilter(
        field_name="rol__nietnatuurlijkpersoon__ann_identificatie",
        help_text=get_help_text("zaken.NietNatuurlijkPersoon", "ann_identificatie"),
        max_length=get_field_attribute(
            "zaken.NietNatuurlijkPersoon", "ann_identificatie", "max_length"
        ),
    )
    rol__betrokkene_identificatie__vestiging__vestigings_nummer = filters.CharFilter(
        field_name="rol__vestiging__vestigings_nummer",
        help_text=get_help_text("zaken.Vestiging", "vestigings_nummer"),
        max_length=get_field_attribute(
            "zaken.Vestiging", "vestigings_nummer", "max_length"
        ),
    )
    rol__betrokkene_identificatie__medewerker__identificatie = filters.CharFilter(
        field_name="rol__medewerker__identificatie",
        help_text=get_help_text("zaken.Medewerker", "identificatie"),
        max_length=get_field_attribute(
            "zaken.Medewerker", "identificatie", "max_length"
        ),
    )
    rol__betrokkene_identificatie__organisatorische_eenheid__identificatie = filters.CharFilter(
        field_name="rol__organisatorischeeenheid__identificatie",
        help_text=get_help_text("zaken.OrganisatorischeEenheid", "identificatie"),
    )
    ordering = filters.OrderingFilter(
        fields=(
            "startdatum",
            "einddatum",
            "publicatiedatum",
            "archiefactiedatum",
            "registratiedatum",
            "identificatie",
        ),
        help_text=_("Het veld waarop de resultaten geordend worden."),
    )

    class Meta:
        model = Zaak
        fields = {
            "identificatie": ["exact"],
            "bronorganisatie": ["exact", "in"],
            "zaaktype": ["exact"],
            "archiefnominatie": ["exact", "in"],
            "archiefactiedatum": ["exact", "lt", "gt", "isnull"],
            "archiefstatus": ["exact", "in"],
            "startdatum": ["exact", "gt", "gte", "lt", "lte"],
            "registratiedatum": ["exact", "gt", "lt"],
            "einddatum": ["exact", "gt", "lt", "isnull"],
            "einddatum_gepland": ["exact", "gt", "lt"],
            "uiterlijke_einddatum_afdoening": ["exact", "gt", "lt"],
            # filters for werkvoorraad
            "rol__betrokkene_type": ["exact"],
            "rol__betrokkene": ["exact"],
            "rol__omschrijving_generiek": ["exact"],
        }


class RolFilter(FilterSet):
    betrokkene_identificatie__natuurlijk_persoon__inp_bsn = filters.CharFilter(
        field_name="natuurlijkpersoon__inp_bsn",
        help_text=get_help_text("zaken.NatuurlijkPersoon", "inp_bsn"),
    )
    betrokkene_identificatie__natuurlijk_persoon__anp_identificatie = filters.CharFilter(
        field_name="natuurlijkpersoon__anp_identificatie",
        help_text=get_help_text("zaken.NatuurlijkPersoon", "anp_identificatie"),
    )
    betrokkene_identificatie__natuurlijk_persoon__inp_a_nummer = filters.CharFilter(
        field_name="natuurlijkpersoon__inp_a_nummer",
        help_text=get_help_text("zaken.NatuurlijkPersoon", "inp_a_nummer"),
    )
    betrokkene_identificatie__niet_natuurlijk_persoon__inn_nnp_id = filters.CharFilter(
        field_name="nietnatuurlijkpersoon__inn_nnp_id",
        help_text=get_help_text("zaken.NietNatuurlijkPersoon", "inn_nnp_id"),
    )
    betrokkene_identificatie__niet_natuurlijk_persoon__ann_identificatie = filters.CharFilter(
        field_name="nietnatuurlijkpersoon__ann_identificatie",
        help_text=get_help_text("zaken.NietNatuurlijkPersoon", "ann_identificatie"),
    )
    betrokkene_identificatie__vestiging__vestigings_nummer = filters.CharFilter(
        field_name="vestiging__vestigings_nummer",
        help_text=get_help_text("zaken.Vestiging", "vestigings_nummer"),
    )
    betrokkene_identificatie__organisatorische_eenheid__identificatie = filters.CharFilter(
        field_name="organisatorischeeenheid__identificatie",
        help_text=get_help_text("zaken.OrganisatorischeEenheid", "identificatie"),
    )
    betrokkene_identificatie__medewerker__identificatie = filters.CharFilter(
        field_name="medewerker__identificatie",
        help_text=get_help_text("zaken.Medewerker", "identificatie"),
    )

    class Meta:
        model = Rol
        fields = (
            "zaak",
            "betrokkene",
            "betrokkene_type",
            "betrokkene_identificatie__natuurlijk_persoon__inp_bsn",
            "betrokkene_identificatie__natuurlijk_persoon__anp_identificatie",
            "betrokkene_identificatie__natuurlijk_persoon__inp_a_nummer",
            "betrokkene_identificatie__niet_natuurlijk_persoon__inn_nnp_id",
            "betrokkene_identificatie__niet_natuurlijk_persoon__ann_identificatie",
            "betrokkene_identificatie__vestiging__vestigings_nummer",
            "betrokkene_identificatie__organisatorische_eenheid__identificatie",
            "betrokkene_identificatie__medewerker__identificatie",
            "roltype",
            "omschrijving",
            "omschrijving_generiek",
        )


class StatusFilter(FilterSet):
    indicatie_laatst_gezette_status = filters.BooleanFilter(
        method="filter_is_last_status",
        help_text=_(
            "Het gegeven is afleidbaar uit de historie van de attribuutsoort Datum "
            "status gezet van van alle statussen bij de desbetreffende zaak."
        ),
    )

    class Meta:
        model = Status
        fields = ("zaak", "statustype", "indicatie_laatst_gezette_status")

    def filter_is_last_status(self, queryset, name, value):
        if value is True:
            return queryset.filter(
                datum_status_gezet=models.F("max_datum_status_gezet")
            )

        if value is False:
            return queryset.exclude(
                datum_status_gezet=models.F("max_datum_status_gezet")
            )

        return queryset.none()


class ResultaatFilter(FilterSet):
    class Meta:
        model = Resultaat
        fields = ("zaak", "resultaattype")


class FkOrUrlOrCMISFieldFilter(FkOrUrlFieldFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        parsed = urlparse(value)
        host = self.parent.request.get_host()

        local = parsed.netloc == host
        if settings.CMIS_ENABLED:
            local = False

        # introspect field to build filter
        model_field = self.model._meta.get_field(self.field_name)

        if local:
            local_object = get_resource_for_path(parsed.path)
            if self.instance_path:
                for bit in self.instance_path.split("."):
                    local_object = getattr(local_object, bit)
            filters = {f"{model_field.fk_field}__{self.lookup_expr}": local_object}
        else:
            filters = {f"{model_field.url_field}__{self.lookup_expr}": value}

        qs = self.get_method(qs)(**filters)
        return qs.distinct() if self.distinct else qs


class ZaakInformatieObjectFilter(FilterSet):
    informatieobject = FkOrUrlOrCMISFieldFilter(
        queryset=ZaakInformatieObject.objects.all(),
        instance_path="canonical",
        help_text=get_help_text("zaken.ZaakInformatieObject", "informatieobject"),
    )

    class Meta:
        model = ZaakInformatieObject
        fields = ("zaak", "informatieobject")


class ZaakObjectFilter(FilterSet):
    class Meta:
        model = ZaakObject
        fields = ("zaak", "object", "object_type")


class KlantContactFilter(FilterSet):
    class Meta:
        model = KlantContact
        fields = ("zaak",)


class ZaakContactMomentFilter(FilterSet):
    class Meta:
        model = ZaakContactMoment
        fields = ("zaak", "contactmoment")


class ZaakVerzoekFilter(FilterSet):
    class Meta:
        model = ZaakVerzoek
        fields = ("zaak", "verzoek")
