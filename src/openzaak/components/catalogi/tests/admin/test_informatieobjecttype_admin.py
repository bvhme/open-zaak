# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2020 Dimpact
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import ngettext_lazy

from django_webtest import WebTest
from freezegun import freeze_time

from openzaak.accounts.tests.factories import SuperUserFactory
from openzaak.notifications.tests.mixins import NotificationsConfigMixin

from ...models import InformatieObjectType, ZaakType, ZaakTypeInformatieObjectType
from ..factories import (
    CatalogusFactory,
    InformatieObjectTypeFactory,
    ZaakTypeFactory,
    ZaakTypeInformatieObjectTypeFactory,
)


class ZiotFilterAdminTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        super().setUp()

        self.app.set_user(self.user)

        self.catalogus = CatalogusFactory.create()

        # Delete automatically created ZaakTypen
        ZaakType.objects.all().delete()
        self.zaaktype = ZaakTypeFactory.create(catalogus=self.catalogus)
        ZaakTypeFactory.create_batch(3, catalogus=CatalogusFactory.create())

    def test_create_ziot_zaaktype_popup_filter_no_catalogus(self):
        response = self.app.get(
            reverse("admin:catalogi_zaaktypeinformatieobjecttype_add")
        )

        popup_zaaktypen = response.html.find("a", {"id": "lookup_id_zaaktype"})
        self.assertEqual(
            popup_zaaktypen.attrs["href"],
            f'{reverse("admin:catalogi_zaaktype_changelist")}?{urlencode({"_to_field": "id"})}',
        )
        # Verify that the popup screen shows only one Zaaktype
        popup_response = self.app.get(popup_zaaktypen.attrs["href"])

        rows = popup_response.html.findAll("tr")[1:]
        self.assertEqual(len(rows), 4)

    def test_create_ziot_zaaktype_popup_filter_with_catalogus(self):
        query_params = urlencode(
            {"catalogus_id__exact": self.catalogus.pk, "catalogus": self.catalogus.pk,}
        )
        url = f'{reverse("admin:catalogi_zaaktypeinformatieobjecttype_add")}?{query_params}'
        response = self.app.get(url)

        popup_zaaktypen = response.html.find("a", {"id": "lookup_id_zaaktype"})
        zaaktype_changelist_url = reverse("admin:catalogi_zaaktype_changelist")
        query_params = urlencode(
            {"_to_field": "id", "catalogus__exact": self.catalogus.pk}
        )
        self.assertEqual(
            popup_zaaktypen.attrs["href"], f"{zaaktype_changelist_url}?{query_params}",
        )
        popup_response = self.app.get(popup_zaaktypen.attrs["href"])
        rows = popup_response.html.findAll("tr")[1:]
        self.assertEqual(len(rows), 1)

    def test_change_ziot_zaaktype_popup_filter(self):
        ziot = ZaakTypeInformatieObjectTypeFactory.create(
            zaaktype=self.zaaktype, informatieobjecttype__catalogus=self.catalogus
        )
        response = self.app.get(
            reverse(
                "admin:catalogi_zaaktypeinformatieobjecttype_change", args=(ziot.pk,)
            )
        )

        popup_zaaktypen = response.html.find("a", {"id": "lookup_id_zaaktype"})
        zaaktype_changelist_url = reverse("admin:catalogi_zaaktype_changelist")
        query_param = urlencode(
            {"_to_field": "id", "catalogus__exact": self.catalogus.pk}
        )
        self.assertEqual(
            popup_zaaktypen.attrs["href"], f"{zaaktype_changelist_url}?{query_param}",
        )
        popup_response = self.app.get(popup_zaaktypen.attrs["href"])
        rows = popup_response.html.findAll("tr")[1:]
        self.assertEqual(len(rows), 1)

    def test_read_published_ziot_zaaktype_popup_filter(self):
        """
        There should be no popup links visible here, because the resource
        is published (and thus read only)
        """
        ziot = ZaakTypeInformatieObjectTypeFactory.create(
            zaaktype__concept=False, informatieobjecttype__concept=False
        )
        response = self.app.get(
            reverse(
                "admin:catalogi_zaaktypeinformatieobjecttype_change", args=(ziot.pk,)
            )
        )

        popup_zaaktypen = response.html.find("a", {"id": "lookup_id_zaaktype"})
        self.assertIsNone(popup_zaaktypen)


class AddZiotAdminTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        super().setUp()

        self.app.set_user(self.user)

        self.catalogus = CatalogusFactory.create()

        # Delete automatically created ZaakTypen
        ZaakType.objects.all().delete()
        self.zaaktype = ZaakTypeFactory.create(catalogus=self.catalogus)

    def test_add_ziot(self):
        iot = InformatieObjectTypeFactory.create(catalogus=self.catalogus, zaaktypen=[])
        url = reverse("admin:catalogi_zaaktypeinformatieobjecttype_add")

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

        form = response.forms["zaaktypeinformatieobjecttype_form"]
        form["volgnummer"] = 1
        form["richting"] = "intern"
        form["zaaktype"] = self.zaaktype.id
        form["informatieobjecttype"] = iot.id

        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ZaakTypeInformatieObjectType.objects.count(), 1)


class IoTypePublishAdminTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        super().setUp()

        self.app.set_user(self.user)

        self.catalogus = CatalogusFactory.create()
        self.url = reverse_lazy("admin:catalogi_informatieobjecttype_changelist")
        self.query_params = {"catalogus_id__exact": self.catalogus.pk}

    def test_publish_selected_success(self):
        iotype1, iotype2 = InformatieObjectTypeFactory.create_batch(
            2, catalogus=self.catalogus
        )

        response = self.app.get(self.url, self.query_params)

        form = response.forms["changelist-form"]
        form["action"] = "publish_selected"
        form["_selected_action"] = [iotype1.pk]

        response = form.submit()

        self.assertEqual(response.status_code, 302)

        messages = [str(m) for m in response.follow().context["messages"]]
        self.assertEqual(
            messages,
            [
                ngettext_lazy(
                    "%d object has been published successfully",
                    "%d objects has been published successfully",
                    1,
                )
                % 1
            ],
        )

        iotype1.refresh_from_db()
        self.assertFalse(iotype1.concept)

        iotype2.refresh_from_db()
        self.assertTrue(iotype2.concept)

    def test_publish_already_selected(self):
        iotype = InformatieObjectTypeFactory.create(
            catalogus=self.catalogus, concept=False
        )

        response = self.app.get(self.url, self.query_params)

        form = response.forms["changelist-form"]
        form["action"] = "publish_selected"
        form["_selected_action"] = [iotype.pk]

        response = form.submit()

        messages = [str(m) for m in response.follow().context["messages"]]
        self.assertEqual(
            messages,
            [
                ngettext_lazy(
                    "%d object is already published",
                    "%d objects are already published",
                    1,
                )
                % 1
            ],
        )

        iotype.refresh_from_db()
        self.assertFalse(iotype.concept)


class CreateIotypeTests(NotificationsConfigMixin, WebTest):
    url = reverse_lazy("admin:catalogi_informatieobjecttype_add")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = SuperUserFactory.create()

    @override_settings(NOTIFICATIONS_DISABLED=False)
    @freeze_time("2022-01-01")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_create_notification_actie(self, mock_notif):
        catalogus = CatalogusFactory.create()
        self.app.set_user(self.user)

        response = self.app.get(self.url)

        form = response.form
        form["omschrijving"] = "test"
        form["vertrouwelijkheidaanduiding"] = "openbaar"
        form["catalogus"] = catalogus.id
        form["datum_begin_geldigheid"] = "2021-10-20"

        with self.captureOnCommitCallbacks(execute=True):
            response = form.submit()

        self.assertEqual(response.status_code, 302)

        iotype = InformatieObjectType.objects.get()
        iotype_url = reverse(
            "informatieobjecttype-detail", kwargs={"uuid": iotype.uuid, "version": 1}
        )
        catalogus_url = reverse(
            "catalogus-detail", kwargs={"uuid": catalogus.uuid, "version": 1}
        )
        mock_notif.assert_called_with(
            {
                "aanmaakdatum": "2022-01-01T00:00:00Z",
                "actie": "create",
                "hoofdObject": f"http://testserver{iotype_url}",
                "kanaal": "informatieobjecttypen",
                "resource": "informatieobjecttype",
                "resourceUrl": f"http://testserver{iotype_url}",
                "kenmerken": {"catalogus": f"http://testserver{catalogus_url}",},
            }
        )
