from rest_framework import serializers
from app.models import Support, Account


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ['id', 'user', 'subject', 'description', 'image', 'status', 'created_at']





class AccountActivationSerializer(serializers.Serializer):
    receipt = serializers.ImageField(required=True)


