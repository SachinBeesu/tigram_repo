from rest_framework import serializers
from my_app.models import *


class RejectApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicationform
        fields = ['reason_office']