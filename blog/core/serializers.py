from rest_framework import serializers


class EmptySerializer(serializers.Serializer):
    """
    Serializer shortcut to use with DestroyAPIView to supress swagger warning
    """

    pass
