import json
from django.test import TestCase

from api.models import Did


class DidAPITest(TestCase):
    base_url = '/api/did/{}/'

    def test_get_returns_json_200(self):
        did_ = Did.objects.create()
        response = self.client.get(self.base_url.format(did_.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
