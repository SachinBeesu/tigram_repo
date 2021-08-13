from rest_framework import serializers
from my_app.models import CustomUser
from django.http import JsonResponse
from django.contrib.auth import authenticate



#user Serializer
class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ('id','phone','name','email','address','photo_proof_name','photo_proof_no','photo_proof_img')

#Register Serializer

class RegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ('id','phone','name','email','password','address','photo_proof_name','photo_proof_no','photo_proof_img')
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		print(validated_data,"*(*(*(*(")
		customuser = CustomUser.objects.create_user(address = validated_data['address'],photo_proof_name = validated_data['photo_proof_name'],photo_proof_no = validated_data['photo_proof_no'],phone =validated_data['phone'],name=validated_data['name'],email=validated_data["email"],password=validated_data['password'])
		return customuser

#login Serializer
class LoginSerializer(serializers.Serializer):
	class Meta:
		model = CustomUser
		fields = ('id','phone','name','email','password')

	email = serializers.CharField()
	password = serializers.CharField()

	def validate(self,data):
		customuser = authenticate(**data)
		if customuser and customuser.is_active:
			return customuser
		raise serializers.ValidationError("Incorrect Credentials")


