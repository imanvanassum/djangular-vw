import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework_jwt import utils
from rest_framework import status
import time


class BaseTestCase(TestCase):

    def setUp(self):
        self.username = 'Iman'
        self.email = 'whouses@email.com'
        self.password = 'testing123'
        self.user = User.objects.create_user(self.username,self.email,self.password)

        self.data = {
            "username":self.username,
            "password":self.password
        }

    def tearDown(self):
        pass


class ObtainJwtTest(BaseTestCase):

    def test_post_with_creds_gets_200(self):
        response = self.client.post('/jwt-auth/', self.data, format='json')
        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual (response.status_code, status.HTTP_200_OK)
        self.assertEqual (decoded_payload['username'], self.username)
        self.assertEqual (response['content-type'], 'application/json')

    def test_post_with_fakenews_gets_error(self):
        response = self.client.post('/jwt-auth/', {"username":"foo","password":"bar"}, format='json')

        self.assertEqual (response.status_code, status.HTTP_400_BAD_REQUEST)


class RefreshTokenTest(BaseTestCase):

    def test_post_without_token_gets_error(self):
        response = self.client.post('/jwt-refresh/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_live_token_gets_fresh(self):
        response = self.client.post('/jwt-auth/', self.data, format='json')
        decoded_payload = utils.jwt_decode_handler(response.data['token'])
        original_exp = decoded_payload['exp']
        self.token = {"token": response.data['token']}
        time.sleep(2)
        response = self.client.post('/jwt-refresh/', self.token)
        decoded_payload = utils.jwt_decode_handler(response.data['token'])
        refreshed_exp = decoded_payload['exp']

        self.assertTrue (refreshed_exp > original_exp)

    def test_post_with_expired_token_gets_error(self):
        # We're going to get a fresh token, sneakily set the expiration to 1, and then try to refresh with it.
        response = self.client.post('/jwt-auth/', self.data, format='json')
        decoded_payload = utils.jwt_decode_handler(response.data['token'])
        decoded_payload['exp'] = 1
        token = utils.jwt_encode_handler(decoded_payload)
        response = self.client.post('/jwt-refresh/', {'token': token}, format='json')

        self.assertEqual (response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual (response.data['non_field_errors'][0], 'Signature has expired.')


class VerifyTokenTest(BaseTestCase):

    def test_post_without_token_gets_error(self):
        response = self.client.post('/jwt-verify/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_expired_token_gets_error(self):
        # We're going to get a fresh token, sneakily set the expiration to 1, and then try to refresh with it.
        response = self.client.post('/jwt-auth/', self.data, format='json')
        decoded_payload = utils.jwt_decode_handler(response.data['token'])
        decoded_payload['exp'] = 1
        token = utils.jwt_encode_handler(decoded_payload)
        response = self.client.post('/jwt-verify/', {'token': token}, format='json')

        self.assertEqual (response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual (response.data['non_field_errors'][0], 'Signature has expired.')

    def test_post_with_live_token_gets_200(self):
        # We're going to get a fresh token, then verify it and verify that they're identical
        response = self.client.post('/jwt-auth/', self.data, format='json')
        orig_token = response.data['token']
        self.token = {"token": orig_token}
        time.sleep(2)
        response = self.client.post('/jwt-verify/', self.token)
        verified_token = response.data['token']

        self.assertEqual (orig_token,verified_token)
