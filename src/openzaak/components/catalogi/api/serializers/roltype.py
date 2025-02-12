# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
from drf_writable_nested import NestedCreateMixin
from rest_framework import serializers
from vng_api_common.constants import RolOmschrijving
from vng_api_common.serializers import add_choice_values_help_text
from vng_api_common.utils import get_help_text

from ...models import RolType
from ..validators import ZaakTypeConceptValidator


class RolTypeSerializer(NestedCreateMixin, serializers.HyperlinkedModelSerializer):
    catalogus = serializers.HyperlinkedRelatedField(
        view_name="catalogus-detail",
        source="zaaktype.catalogus",
        read_only=True,
        lookup_field="uuid",
        help_text=get_help_text("catalogi.ZaakType", "catalogus"),
    )

    class Meta:
        model = RolType
        fields = (
            "url",
            "zaaktype",
            "omschrijving",
            "omschrijving_generiek",
            "catalogus",
        )
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "zaaktype": {"lookup_field": "uuid"},
        }
        validators = [ZaakTypeConceptValidator()]

    def get_fields(self):
        fields = super().get_fields()

        value_display_mapping = add_choice_values_help_text(RolOmschrijving)
        fields["omschrijving_generiek"].help_text += f"\n\n{value_display_mapping}"

        return fields
