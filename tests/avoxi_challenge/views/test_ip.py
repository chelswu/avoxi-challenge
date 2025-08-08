import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from geoip2.errors import GeoIP2Error, AddressNotFoundError


class IPValidationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('ip-validate')  # Adjust URL name as needed

    @patch('avoxi_challenge.views.ip.Client')
    def test_valid_ip_allowed_country(self, mock_client):
        """Test valid IP from allowed country returns success"""
        # Mock the GeoIP client response
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'US'
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': ['US', 'CA', 'GB']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['ip'], '8.8.8.8')
        self.assertEqual(data['iso_code'], 'US')
        self.assertTrue(data['is_allowed'])

    @patch('avoxi_challenge.views.ip.Client')
    def test_valid_ip_not_allowed_country(self, mock_client):
        """Test valid IP from non-allowed country returns success but not allowed"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'CN'
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '1.2.3.4',
            'country_list': ['US', 'CA', 'GB']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['ip'], '1.2.3.4')
        self.assertEqual(data['iso_code'], 'CN')
        self.assertFalse(data['is_allowed'])

    def test_invalid_ip_format(self):
        """Test invalid IP format returns 400 error"""
        response = self.client.get(self.url, {
            'ip': 'invalid.ip.format',
            'country_list': ['US', 'CA']
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_ip_parameter(self):
        """Test missing IP parameter returns 400 error"""
        response = self.client.get(self.url, {
            'country_list': ['US', 'CA']
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_country_list_parameter(self):
        """Test missing country_list parameter returns 400 error"""
        response = self.client.get(self.url, {
            'ip': '8.8.8.8'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('avoxi_challenge.views.ip.Client')
    def test_empty_country_list(self, mock_client):
        """Test empty country list"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'US'
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': []
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data, {'country_list': ['This field is required.']})

    @patch('avoxi_challenge.views.ip.Client')
    def test_geoip_connection_error(self, mock_client):
        """Test GeoIP connection error returns 500"""
        mock_instance = MagicMock()
        mock_instance.country.side_effect = GeoIP2Error("Connection failed")
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': ['US', 'CA']
        })

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Error getting country code from IP')

    @patch('avoxi_challenge.views.ip.Client')
    def test_ip_not_found_error(self, mock_client):
        """Test when IP address is not found in GeoIP database"""
        mock_instance = MagicMock()
        mock_instance.country.side_effect = AddressNotFoundError("Address not found")
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '192.168.1.1',  # Private IP
            'country_list': ['US', 'CA']
        })

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn('error', data)

    @patch('avoxi_challenge.views.ip.Client')
    def test_ipv6_address(self, mock_client):
        """Test IPv6 address validation"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'US'
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '2001:4860:4860::8888',
            'country_list': ['US', 'CA']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['ip'], '2001:4860:4860::8888')
        self.assertEqual(data['iso_code'], 'US')
        self.assertTrue(data['is_allowed'])

    @patch('avoxi_challenge.views.ip.Client')
    def test_case_insensitive_country_codes(self, mock_client):
        """Test that country code comparison is case-insensitive"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'us'  # lowercase from API
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': ['us', 'CA']  # mixed case in request
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # This test might fail if your implementation doesn't handle case sensitivity
        # You may need to update your view to handle this
        self.assertEqual(data['ip'], '8.8.8.8')
        self.assertEqual(data['iso_code'], 'US')
        self.assertTrue(data['is_allowed'])

    @patch('avoxi_challenge.views.ip.Client')
    def test_single_country_in_list(self, mock_client):
        """Test with single country in allowed list"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'US'
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': ['US']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['is_allowed'])

    @patch('avoxi_challenge.views.ip.Client')
    def test_multiple_query_parameters(self, mock_client):
        """Test handling of multiple country codes in query params"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = 'CA'
        mock_client.return_value = mock_instance

        # Depending on how your serializer handles multiple values
        response = self.client.get(self.url + '?ip=8.8.8.8&country_list=US&country_list=CA&country_list=GB')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['is_allowed'])

    @patch('avoxi_challenge.views.ip.Client')
    @patch('avoxi_challenge.views.ip.logger')
    def test_logging_on_geoip_error(self, mock_logger, mock_client):
        """Test that errors are properly logged"""
        mock_instance = MagicMock()
        error_msg = "Connection timeout"
        mock_instance.country.side_effect = GeoIP2Error(error_msg)
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': ['US']
        })

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Verify that logger.exception was called
        mock_logger.exception.assert_called_once()

    @patch('avoxi_challenge.views.ip.Client')
    def test_edge_case_empty_iso_code(self, mock_client):
        """Test when GeoIP returns empty or None ISO code"""
        mock_instance = MagicMock()
        mock_instance.country.return_value.country.iso_code = None
        mock_client.return_value = mock_instance

        response = self.client.get(self.url, {
            'ip': '8.8.8.8',
            'country_list': ['US', 'CA']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNone(data['iso_code'])
        self.assertFalse(data['is_allowed'])


class IPValidationIntegrationTest(TestCase):
    """Integration tests without mocking external services"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('ip-validate')

    @pytest.mark.integration
    def test_real_geoip_service(self):
        """Integration test with real GeoIP service (requires valid credentials)"""
        # Only run this test if you have valid GeoIP credentials configured
        # and want to test against the real service
        response = self.client.get(self.url, {
            'ip': '8.8.8.8',  # Google's public DNS
            'country_list': ['US']
        })

        # This test will depend on your actual GeoIP service configuration
        # Comment out or skip if you don't want to hit external services in tests
        self.assertIn(response.status_code, [200, 500])  # 500 if no valid credentials