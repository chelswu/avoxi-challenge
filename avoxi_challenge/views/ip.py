from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from geoip2.webservice import Client
from rest_framework import status
from rest_framework.views import APIView

from django.conf import settings
from avoxi_challenge.serializers.ip import IPValidationSerializer, IPValidationResponseSerializer

class IPValidationView(APIView):
    """
    Validate the given IP address against a list of allowed countries
    """
    @swagger_auto_schema(
        operation_description="Validate the given IP address against a list of allowed countries.  See https://www.geonames.org/countries/ to get the correct country code from the ISO-3166 alpha2 column",
        query_serializer=IPValidationSerializer,
        responses={
            200: IPValidationResponseSerializer,
            400: "Bad Request",
        },
    )
    def get(self, request):
        serializer = IPValidationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        geolite_client = Client(settings.GEO_IP_ACCOUNT, settings.GEO_IP_LICENSE, host="geolite.info")
        geolite_response = geolite_client.country(serializer.validated_data["ip"])
        iso_code = geolite_response.country.iso_code

        response_serializer = IPValidationResponseSerializer(data={
            "ip": serializer.validated_data["ip"],
            "iso_code": iso_code,
            "is_allowed": iso_code in serializer.validated_data["country_list"],
        })
        response_serializer.is_valid(raise_exception=True)
        return JsonResponse(response_serializer.data, status=status.HTTP_200_OK)