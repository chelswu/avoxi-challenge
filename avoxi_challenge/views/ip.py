from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from avoxi_challenge.serializers.IPSerializers import IPValidationSerializer, IPValidationResponseSerializer

class IPValidationView(APIView):
    """
    Validate the given IP address against a list of allowed countries
    """
    @swagger_auto_schema(
        operation_description="Validate the given IP address against a list of allowed countries",
        query_serializer=IPValidationSerializer,
        responses={
            200: IPValidationResponseSerializer,
            400: "Bad Request",
        },
    )
    def get(self, request):
        serializer = IPValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: use geolite APIs to check ip address
        response_serializer = IPValidationResponseSerializer(data={})
        return JsonResponse(response_serializer.data, status=status.HTTP_200_OK)