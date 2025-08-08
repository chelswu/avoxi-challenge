from rest_framework import serializers


class IPValidationSerializer(serializers.Serializer):
    ip = serializers.IPAddressField(help_text="IP address to validate")
    country_list = serializers.ListField(child=serializers.CharField(), help_text="List of allowed country codes in ISO-3166 alpha2 format")


class IPValidationResponseSerializer(serializers.Serializer):
    ip = serializers.IPAddressField(help_text="IP address that was validated")
    iso_code = serializers.CharField(help_text="Country code for the IP")
    is_allowed = serializers.BooleanField(help_text="Whether the country this IP is coming from is in the list of allowed countries")