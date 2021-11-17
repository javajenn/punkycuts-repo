from rest_framework import serializers
from .models import Screenshot

class ScreenshotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = [
            'screenshot'
        ]