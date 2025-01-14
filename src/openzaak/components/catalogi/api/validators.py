# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ErrorDetail
from rest_framework.serializers import Serializer, ValidationError
from vng_api_common.constants import (
    Archiefnominatie,
    BrondatumArchiefprocedureAfleidingswijze as Afleidingswijze,
)

from openzaak.client import fetch_object
from openzaak.components.catalogi.api.scopes import SCOPE_CATALOGI_FORCED_WRITE
from openzaak.utils.serializers import get_from_serializer_data_or_instance

from ..constants import SelectielijstKlasseProcestermijn as Procestermijn
from ..utils import has_overlapping_objects
from ..validators import validate_brondatumarchiefprocedure


class GeldigheidValidator:
    """
    Validate that the (new) object is unique between a start and end date.

    Empty end date is an open interval, which means that the object cannot
    be created after the start date.
    """

    code = "overlap"
    message = _(
        "Dit {} komt al voor binnen de catalogus en opgegeven geldigheidsperiode."
    )
    requires_context = True

    def __init__(self, omschrijving_field="omschrijving"):
        self.omschrijving_field = omschrijving_field

    def __call__(self, attrs, serializer):
        # Determine the existing instance, if this is an update operation.
        instance = getattr(serializer, "instance", None)
        base_model = getattr(serializer.Meta, "model", None)

        catalogus = get_from_serializer_data_or_instance("catalogus", attrs, serializer)
        begin_geldigheid = get_from_serializer_data_or_instance(
            "begin_geldigheid", attrs, serializer
        )
        einde_geldigheid = get_from_serializer_data_or_instance(
            "einde_geldigheid", attrs, serializer
        )
        omschrijving = get_from_serializer_data_or_instance(
            "omschrijving", attrs, serializer
        )

        if has_overlapping_objects(
            model_manager=base_model._default_manager,
            catalogus=catalogus,
            omschrijving_query={self.omschrijving_field: omschrijving},
            begin_geldigheid=begin_geldigheid,
            einde_geldigheid=einde_geldigheid,
            instance=instance,
        ):
            # are we patching eindeGeldigheid?
            changing_published_geldigheid = serializer.partial and list(attrs) == [
                "datum_einde_geldigheid"
            ]
            error_field = (
                "einde_geldigheid"
                if changing_published_geldigheid
                else "begin_geldigheid"
            )
            raise ValidationError(
                {error_field: self.message.format(base_model._meta.verbose_name)},
                code=self.code,
            )


class RelationCatalogValidator:
    code = "relations-incorrect-catalogus"
    message = _("The {} has catalogus different from created object")

    def __init__(self, relation_field: str, catalogus_field="catalogus"):
        self.relation_field = relation_field
        self.catalogus_field = catalogus_field

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs: dict):
        relations = attrs.get(self.relation_field)
        catalogus = attrs.get(self.catalogus_field) or self.instance.catalogus

        if not relations:
            return

        if not isinstance(relations, list):
            relations = [relations]

        for relation in relations:
            if relation.catalogus != catalogus:
                raise ValidationError(
                    self.message.format(self.relation_field), code=self.code
                )


class ProcesTypeValidator:
    code = "procestype-mismatch"
    message = _("{} should belong to the same procestype as {}")

    def __init__(self, relation_field: str, zaaktype_field="zaaktype"):
        self.relation_field = relation_field
        self.zaaktype_field = zaaktype_field

    def __call__(self, attrs: dict):
        selectielijstklasse_url = attrs.get(self.relation_field)
        zaaktype = attrs.get(self.zaaktype_field)

        if not selectielijstklasse_url:
            return

        selectielijstklasse = fetch_object("resultaat", selectielijstklasse_url)

        if selectielijstklasse["procesType"] != zaaktype.selectielijst_procestype:
            raise ValidationError(
                self.message.format(self.relation_field, self.zaaktype_field),
                code=self.code,
            )


class ProcestermijnAfleidingswijzeValidator:
    code = "invalid-afleidingswijze-for-procestermijn"
    message = _(
        "afleidingswijze cannot be {} when selectielijstklasse.procestermijn is {}"
    )

    def __init__(
        self,
        selectielijstklasse_field: str,
        archiefprocedure_field="brondatum_archiefprocedure",
    ):
        self.selectielijstklasse_field = selectielijstklasse_field
        self.archiefprocedure_field = archiefprocedure_field

    def __call__(self, attrs: dict):
        selectielijstklasse_url = attrs.get(self.selectielijstklasse_field)
        archiefprocedure = attrs.get(self.archiefprocedure_field)

        if not selectielijstklasse_url or not archiefprocedure:
            return

        selectielijstklasse = fetch_object("resultaat", selectielijstklasse_url)
        procestermijn = selectielijstklasse["procestermijn"]
        afleidingswijze = archiefprocedure["afleidingswijze"]

        error = False

        if not procestermijn:
            return

        if (
            procestermijn == Procestermijn.nihil
            and afleidingswijze != Afleidingswijze.afgehandeld
        ) or (
            procestermijn != Procestermijn.nihil
            and afleidingswijze == Afleidingswijze.afgehandeld
        ):
            error = True
        elif (
            procestermijn == Procestermijn.ingeschatte_bestaansduur_procesobject
            and afleidingswijze != Afleidingswijze.termijn
        ) or (
            procestermijn != Procestermijn.ingeschatte_bestaansduur_procesobject
            and afleidingswijze == Afleidingswijze.termijn
        ):
            error = True

        if error:
            raise ValidationError(
                self.message.format(afleidingswijze, procestermijn), code=self.code
            )


class BrondatumArchiefprocedureValidator:
    empty_code = "must-be-empty"
    empty_message = _("This field must be empty for afleidingswijze `{}`")
    required_code = "required"
    required_message = _("This field is required for afleidingswijze `{}`")
    requires_context = True

    def __init__(self, archiefprocedure_field="brondatum_archiefprocedure"):
        self.archiefprocedure_field = archiefprocedure_field

    def __call__(self, attrs: dict, serializer: Serializer):
        instance = getattr(serializer, "instance", None)
        partial = getattr(serializer, "partial", None)
        archiefprocedure = attrs.get(self.archiefprocedure_field)
        if archiefprocedure is None:
            archiefnominatie = attrs.get(
                "archiefnominatie", getattr(instance, "archiefnominatie", None)
            )
            if not partial and archiefnominatie != Archiefnominatie.blijvend_bewaren:
                raise ValidationError(
                    {
                        self.archiefprocedure_field: _(
                            "This field is required if archiefnominatie is {an}"
                        ).format(an=archiefnominatie)
                    },
                    code="required",
                )
            return

        afleidingswijze = archiefprocedure["afleidingswijze"]
        error, empty, required = validate_brondatumarchiefprocedure(archiefprocedure)

        if error:
            error_dict = {}
            for fieldname in empty:
                error_dict.update(
                    {
                        f"{self.archiefprocedure_field}.{fieldname}": ErrorDetail(
                            self.empty_message.format(afleidingswijze), self.empty_code
                        )
                    }
                )
            for fieldname in required:
                error_dict.update(
                    {
                        f"{self.archiefprocedure_field}.{fieldname}": ErrorDetail(
                            self.required_message.format(afleidingswijze),
                            self.required_code,
                        )
                    }
                )
            raise ValidationError(error_dict)


class ZaakTypeInformatieObjectTypeCatalogusValidator:
    code = "relations-incorrect-catalogus"
    message = _("The zaaktype has catalogus different from informatieobjecttype")

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs: dict):
        zaaktype = attrs.get("zaaktype") or self.instance.zaaktype
        informatieobjecttype = (
            attrs.get("informatieobjecttype") or self.instance.informatieobjecttype
        )

        if zaaktype.catalogus != informatieobjecttype.catalogus:
            raise ValidationError(self.message, code=self.code)


class DeelzaaktypeCatalogusValidator:
    code = "relations-incorrect-catalogus"
    message = _("Hoofd- en deelzaaktypen moeten tot dezelfde catalogus behoren")

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.instance = serializer.instance

    def __call__(self, attrs: dict):
        default_deelzaaktypen = (
            self.instance.deelzaaktypen.all() if self.instance else []
        )
        default_catalogus = self.instance.catalogus if self.instance else None

        deelzaaktypen = attrs.get("deelzaaktypen") or default_deelzaaktypen
        catalogus = attrs.get("catalogus") or default_catalogus

        # can't run validator...
        if catalogus is None:
            return

        if any(
            deelzaaktype.catalogus_id != catalogus.id for deelzaaktype in deelzaaktypen
        ):
            raise ValidationError({"deelzaaktypen": self.message}, code=self.code)


def is_force_write(serializer) -> bool:
    request = serializer.context["request"]

    # if no jwt_auth -> it's used in the admin of the management command
    if not hasattr(request, "jwt_auth"):
        return True

    return request.jwt_auth.has_auth(
        scopes=SCOPE_CATALOGI_FORCED_WRITE,
        init_component=serializer.Meta.model._meta.app_label,
    )


class ConceptUpdateValidator:
    message = _("Het is niet toegestaan om een non-concept object bij te werken")
    code = "non-concept-object"
    requires_context = True

    def __call__(self, attrs, serializer):
        # Determine the existing instance, if this is an update operation.
        instance = getattr(serializer, "instance", None)

        if not instance:
            return

        # New in Catalogi 1.2: allow concept update for a specific scope
        if is_force_write(serializer):
            return

        # updating eindeGeldigheid is allowed through patch requests
        if serializer.partial and list(attrs.keys()) == ["datum_einde_geldigheid"]:
            return

        if not instance.concept:
            raise ValidationError(self.message, code=self.code)


class VerlengingsValidator:
    message = _("Verlengingstermijn must be set if verlengingMogelijk is true")
    code = "verlenging-mismatch"

    def __call__(self, attrs):
        if attrs.get("verlenging_mogelijk") and not attrs.get("verlengingstermijn"):
            raise ValidationError(self.message, code=self.code)


class ZaakTypeConceptValidator:
    """
    Validator that checks for related non-concept zaaktype when doing
    updates/creates
    """

    message = _(
        "Updating an object that has a relation to a non-concept zaaktype is forbidden"
    )
    code = "non-concept-zaaktype"
    requires_context = True

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs, serializer):
        # New in Catalogi 1.2: allow concept update for a specific scope
        if is_force_write(serializer):
            return

        if self.instance:
            zaaktype = self.instance.zaaktype
            if not zaaktype.concept:
                raise ValidationError(self.message, code=self.code)

        zaaktype_in_attrs = attrs.get("zaaktype")
        if zaaktype_in_attrs:
            if not zaaktype_in_attrs.concept:
                msg = _("Creating a relation to non-concept zaaktype is forbidden")
                raise ValidationError(msg, code=self.code)


class M2MConceptCreateValidator:
    """
    Validator that checks for related non-concepts in M2M fields when creating
    objects
    """

    code = "non-concept-relation"
    requires_context = True

    def __init__(self, concept_related_fields):
        self.concept_related_fields = concept_related_fields

    def __call__(self, attrs, serializer):
        # Determine the existing instance, if this is an update operation.
        instance = getattr(serializer, "instance", None)
        if instance:
            return

        # New in Catalogi 1.2: allow concept create for a specific scope
        if is_force_write(serializer):
            return

        for field_name in self.concept_related_fields:
            field = attrs.get(field_name, [])
            for related_object in field:
                if not related_object.concept:
                    msg = _(
                        f"Relations to non-concept {field_name} object can't be created"
                    )
                    raise ValidationError(msg, code=self.code)


class M2MConceptUpdateValidator:
    """
    Validator that checks for related non-concepts in M2M fields when doing
    updates
    """

    code = "non-concept-relation"
    requires_context = True

    def __init__(self, concept_related_fields):
        self.concept_related_fields = concept_related_fields

    def __call__(self, attrs, serializer):
        # Determine the existing instance, if this is an update operation.
        instance = getattr(serializer, "instance", None)
        request = serializer.context["request"]
        if not instance:
            return

        # New in Catalogi 1.2: allow concept update for a specific scope
        if is_force_write(serializer):
            return

        einde_geldigheid = attrs.get("datum_einde_geldigheid")
        if einde_geldigheid and len(request.data) == 1:
            return

        for field_name in self.concept_related_fields:
            field = getattr(instance, field_name)
            related_non_concepts = field.filter(concept=False)
            if related_non_concepts.exists():
                msg = _(f"Objects related to non-concept {field_name} can't be updated")
                raise ValidationError(msg, code=self.code)

            # Validate that no new relations are created to resources with
            # non-concept status
            field_in_attrs = attrs.get(field_name)
            if field_in_attrs:
                for relation in field_in_attrs:
                    if not relation.concept:
                        msg = _(
                            f"Objects can't be updated with a relation to non-concept {field_name}"
                        )
                        raise ValidationError(msg, code=self.code)
