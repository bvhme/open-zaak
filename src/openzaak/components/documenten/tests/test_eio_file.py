"""
Test the flow described in https://github.com/VNG-Realisatie/gemma-zaken/issues/39
"""
import base64
from datetime import date
from urllib.parse import urlparse

from django.test import override_settings

from privates.test import temp_private_root
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import reverse

from openzaak.components.catalogi.models.tests.factories import (
    InformatieObjectTypeFactory,
)
from openzaak.components.documenten.api.tests.utils import get_operation_url
from openzaak.components.documenten.models import EnkelvoudigInformatieObject
from openzaak.components.documenten.models.tests.factories import (
    EnkelvoudigInformatieObjectCanonicalFactory,
    EnkelvoudigInformatieObjectFactory,
)
from openzaak.utils.tests import JWTAuthMixin


@override_settings(SENDFILE_BACKEND="sendfile.backends.simple")
@temp_private_root()
class US39TestCase(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    def test_create_enkelvoudiginformatieobject(self):
        """
        Registreer een ENKELVOUDIGINFORMATIEOBJECT
        """
        informatieobjecttype = InformatieObjectTypeFactory.create()
        informatieobjecttype_url = reverse(informatieobjecttype)
        url = get_operation_url("enkelvoudiginformatieobject_create")
        data = {
            "identificatie": "AMS20180701001",
            "bronorganisatie": "159351741",
            "creatiedatum": "2018-07-01",
            "titel": "text_extra.txt",
            "auteur": "ANONIEM",
            "formaat": "text/plain",
            "taal": "dut",
            "inhoud": base64.b64encode(b"Extra tekst in bijlage").decode("utf-8"),
            "informatieobjecttype": informatieobjecttype_url,
            "vertrouwelijkheidaanduiding": VertrouwelijkheidsAanduiding.openbaar,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        eio = EnkelvoudigInformatieObject.objects.get()

        self.assertEqual(eio.identificatie, "AMS20180701001")
        self.assertEqual(eio.creatiedatum, date(2018, 7, 1))

        download_url = urlparse(response.data["inhoud"])

        self.assertTrue(
            download_url.path,
            get_operation_url("enkelvoudiginformatieobject_download", uuid=eio.uuid),
        )

    def test_read_detail_file(self):
        eio = EnkelvoudigInformatieObjectFactory.create()
        file_url = get_operation_url(
            "enkelvoudiginformatieobject_download", uuid=eio.uuid
        )

        response = self.client.get(file_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode("utf-8"), "some data")

    def test_list_file(self):
        eio = EnkelvoudigInformatieObjectCanonicalFactory.create()
        list_url = get_operation_url("enkelvoudiginformatieobject_list")

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["results"]
        download_url = urlparse(data[0]["inhoud"])

        self.assertEqual(
            download_url.path,
            get_operation_url(
                "enkelvoudiginformatieobject_download", uuid=eio.latest_version.uuid
            ),
        )
