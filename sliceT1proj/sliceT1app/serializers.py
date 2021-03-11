from sliceT1app.models import fileDoc
from rest_framework import serializers


class DocSerializer(serializers.ModelSerializer):
    class Meta:
        model = fileDoc
        fields = ['id','file_id','name','size', 'url', 'file']
        extra_kwargs = {'file_id': {'required': False}}