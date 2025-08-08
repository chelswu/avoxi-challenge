import logging
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from geoip2.errors import GeoIP2Error
from geoip2.webservice import Client
from rest_framework import status
from rest_framework.views import APIView

from django.conf import settings
from avoxi_challenge.serializers.ip import IPValidationSerializer, IPValidationResponseSerializer

logger = logging.getLogger(__name__)

class IPValidationView(APIView):
    """
    Validate the given IP address against a list of allowed countries
    """
    @swagger_auto_schema(
        operation_description="Validate the given IP address against a list of allowed countries.  See https://www.geonames.org/countries/ to get the correct country code from the ISO-3166 alpha2 column",
        manual_parameters=[
            openapi.Parameter(
                'ip',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'country_list',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, max_length=2),
                collection_format='multi',
                required=True
            ),
        ],
        responses={
            200: IPValidationResponseSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request):
        serializer = IPValidationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            geolite_client = Client(settings.GEO_IP_ACCOUNT, settings.GEO_IP_LICENSE, host="geolite.info")
            geolite_response = geolite_client.country(serializer.validated_data["ip"])
            iso_code = geolite_response.country.iso_code.upper() if geolite_response.country.iso_code else None
        except GeoIP2Error as error:
            # We don't want to expose the actual error to the customer, but we still want to log it.
            logger.exception(f"Error connecting to GeoIP client: {error}")
            return JsonResponse({"error": "Error getting country code from IP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_serializer = IPValidationResponseSerializer(data={
            "ip": serializer.validated_data["ip"],
            "iso_code": iso_code,
            "is_allowed": iso_code in serializer.validated_data["country_list"],
        })
        response_serializer.is_valid()
        return JsonResponse(response_serializer.data, status=status.HTTP_200_OK)