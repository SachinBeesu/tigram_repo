from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.hashers import make_password

# Create your views here.
from django.shortcuts import render
import json
from django.http import JsonResponse
from knox.models import AuthToken
from my_app.models import *
from rest_framework.response import Response
from rest_framework import generics,permissions
from rest_framework.views import APIView
from django.contrib.auth  import login,authenticate,logout
from django.contrib.auth.models import Group
import random
import qrcode
import datetime
import string
from rest_framework.permissions import IsAuthenticated

from django.template.loader import get_template
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from xhtml2pdf import pisa 
import os
from .serializers import UserSerializer,RegisterSerializer,LoginSerializer
# Create your views here.
from django.shortcuts import render
from .serializers import *
from rest_framework import generics,permissions
from rest_framework.response import Response
from django.contrib.auth.models import Group
from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from datetime import datetime
import datetime

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,HttpResponseNotFound
from django.db.models.functions import ExtractDay

# Create your views here.
from my_app.models import*
from .serializers import*
from rest_framework import status
from django.db.models.functions import Cast

from django.db.models import Count, Case,Sum, When, CharField,IntegerField,DecimalField,FloatField, F

def generate_app_id(uid,app_id): #uid
    # uid=31254
    # date = datetime.date.today()
    date1 = date.today()
    # gno = '0'*(4-len(str(uid)))
    # uid = str(gno)+str(uid)
    applicant_no = 'TG/'+str(date1.year)+'/'+str(date1.month)+'/'+str(uid)+'/'+str(app_id)
    # print("----")
    # print("---gen-")
    # date1 = datetime.date.today()
    # print(user_id)
    applicant_no = applicant_no.replace('-','')
    return applicant_no


def generate_noc_app_id(uid,app_id): #uid
    # uid=31254
    # date = datetime.date.today()
    date1 = date.today()
    # gno = '0'*(4-len(str(uid)))
    # uid = str(gno)+str(uid)
    applicant_no = 'NOC/'+str(date1.year)+'/'+str(date1.month)+'/'+str(uid)+'/'+str(app_id)
    # print("----")
    # print("---gen-")
    # date1 = datetime.date.today()
    # print(user_id)
    applicant_no = applicant_no.replace('-','')
    return applicant_no


#UserIDGeneration
def generate_user_id(uid): #uid
    # uid=31254
    date1 = date.today()
    gno = '0'*(4-len(str(uid)))
    uid = str(gno)+str(uid)
    user_id = str(date1)+uid
    # print(user_id)
    user_id = user_id.replace('-','')
    return user_id

def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path

class NewLogin(APIView):
    permission_classes = [permissions.AllowAny,]



    def post(self, request):
        print(request.data)
        username = request.data["email_or_phone"]
        password = request.data["password"]
        error = "error"
        from datetime import datetime
        # token, created = Token.objects.get_or_create(user=user)
        if '@' in username:
            user = authenticate(request,email=username,password=password)
            if user:

                _, token = AuthToken.objects.create(user)
                CustomUser.objects.filter(id=user.id).update(login_date=datetime.now())

                status = CustomUser.objects.filter(id=user.id)
                data = UserSerializer(user).data
                groups=user.groups.values_list('name',flat = True)
                print(groups)
                print(user)
                rlist = []
                data["user_group"] = groups
                if "division officer" in groups:
                    grp = groups[0]
                    div = DivisionOfficerdetail.objects.filter(div_user_id = user.id).values('id','division_name__name','division_name__id')
                    print(div)
                    rng = Range.objects.filter(division_id = div[0]["division_name__id"]).values('name')
                    data["division"] =  div
                    
                    for i in rng:
                        rlist.append(i["name"])

                    data["range"] = rlist
                
                if "state officer" in groups:
                    div = StateOfficerdetail.objects.filter(state_user_id = user.id).values('id','state_name')
                    #print(div,"*************************")
                    temp = []
                   
                    if div:
                        div_list = Division.objects.filter(state__name =div[0]["state_name"]).values('id','name')
                        print(div_list)
                        for k in div_list:
                            trp ={}
                 #            
                            trp["division"] = k["name"]
                            rangelst = []
                            arlt = Range.objects.filter(division_id = k["id"]).values_list('name',flat=True)
                            trp["ranges"] =arlt#list(arlt)
                            temp.append(trp)
                            
                          
                        
                    #rng = Range.objects.filter(division_id = div[0]["division_name__id"]).values('name')
                    data["division_range_list"] =  temp
                    
                   # for i in rng:
                    #    rlist.append(i["name"])

                    #data["range"] = rlist
                  
                  
                  
                  
                #img = data["profile_pic"]
                #del data["profile_pic"]

                #if img =="":
                #    data["profile_pic"]  = settings.SERVER_BASE_URL+settings.NO_PROFILE_PATH+img
                #else:
                #    data["profile_pic"]  = settings.SERVER_BASE_URL+settings.PROFILE_PATH+img
                #print(settings.SERVER_BASE_URL+settings.NO_PROFILE_PATH+img)


                content= {
                    "status":"success",
                    "message":"Successfully Login",
                    "data":data,
                    "token":token
                    }
            else:
                content = {
                    "status":"error",
                    "message":"Invalid Credentials"

                }



                # print("email")
        else:
            print("phone")
            eml=""
            em = CustomUser.objects.filter(phone=username).values('email')
            if em:

                print(em[0]["email"])
                eml= em[0]["email"]
            else:
                eml=""
            user = authenticate(email=eml,password=password)
            if user:

                _, token = AuthToken.objects.create(user)
                CustomUser.objects.filter(id=user.id).update(login_date=datetime.now())

                status = CustomUser.objects.filter(id=user.id)
                data = UserSerializer(user).data
                groups=user.groups.values_list('name',flat = True)
                print(groups)
                data["user_group"] = groups
                #img = data["profile_pic"]
                #del data["profile_pic"]

                #if img =="":
                #    data["profile_pic"]  = settings.SERVER_BASE_URL+settings.NO_PROFILE_PATH+img
                #else:
                #    data["profile_pic"]  = settings.SERVER_BASE_URL+settings.PROFILE_PATH+img
                #print(settings.SERVER_BASE_URL+settings.NO_PROFILE_PATH+img)

    
                content= {
                    "status":"success",
                    "message":"Successfully Login",
                    "data":data,
                    "token":token
                    }
            else:
                content = {
                    "status":"error",
                    "message":"Invalid Credentials"

                }

        return Response(content)

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customuser = serializer.validated_data
            _, token = AuthToken.objects.create(customuser)
            CustomUser.objects.filter(id=customuser.id).update(login_date=datetime.now())

            status = CustomUser.objects.filter(id=customuser.id)
            print(status)

            data = UserSerializer(customuser,context=self.get_serializer_context()).data
            groups=customuser.groups.values_list('name',flat = True)
            print(groups)
            data["user_group"] = groups
            img = data["profile_pic"]
            del data["profile_pic"]

            if img =="":
                data["profile_pic"]  = settings.SERVER_BASE_URL+settings.NO_PROFILE_PATH+img
            else:
                data["profile_pic"]  = settings.SERVER_BASE_URL+settings.PROFILE_PATH+img
            print(settings.SERVER_BASE_URL+settings.NO_PROFILE_PATH+img)

   
            return Response({
                "data":data,
                "token":token
                })
        else:
            print(serializer)
            print(serializer.errors)

            return Response({
                "Login":"Denied",
                })



class NewRegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []
    def post(self,request,*args,**kwargs):

        user_type = "user"
        # name = request.data.pop("name")
        # phone = request.data.pop("phone")
        # email = request.data.pop("email")
        # password = request.data.pop("password")
        # address = request.data.pop("address")
        # photo_proof_name = request.data.pop("photo_proof_name")
        # photo_proof_img = request.data.pop("photo_proof_img")
        # photo_proof_type_id = request.data.pop("photo_proof_img")
        photo_proof_img = request.data.pop("photo_proof_img")
        print(request.data)
        phone = request.data["phone"]
        ph_exists = CustomUser.objects.filter(phone = phone)
        if ph_exists:
            
            return Response({
                "status":"Error",
                "Message":"Phone Number Already Exists."
                })
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customuser = serializer.save()
          
            group = Group.objects.get(name=user_type)
            group.user_set.add(customuser)
                        
            otp = ''.join(random.sample("0123456789", 4))
            if photo_proof_img !="":
                generated_id = generate_user_id(customuser.id)
                customuser.user_id = generated_id
                make_id = str(customuser.id)+'r' 
                url = '/static/media/upload/'
                saved_photo=upload_product_image_file(customuser.id,photo_proof_img,url,'PhotoProof')
                customuser.photo_proof_img = saved_photo
                CustomUser.objects.filter(id=customuser.id).update(photo_proof_img=settings.SERVER_BASE_URL + settings.PHOTO_PROOF_PATH+saved_photo)
                print(saved_photo)
                # pf_name = save_img(photo_proof_img,customuser.id)
                # pf_name = settings.SERVER_BASE_URL+settings.PHOTO_PROOF_PATH+pf_name
            else:

                pf_name = settings.SERVER_BASE_URL+settings.NO_IMAGE
            message ="sent"
            send_status = "sent"
            random_otp = "0000"
            otp ="0000"
            # message,send_status,random_otp=send_msg_otp_signup_verification(customuser.phone,customuser.name,otp)
            # status = email(customuser.email,customuser.name,otp)
            # print('Email OTP Status: ',status)
            print('OTP Status ')
            print(send_status)
            # save_otp = SendOtp.objects.create(otp_owner=customuser,otp=otp)
            # save_otp.save()
            data = UserSerializer(customuser,context=self.get_serializer_context()).data
            data["user_type"]=user_type
            # data["profile_image"] = pf_name
            data["photo_proof_img"] = settings.SERVER_BASE_URL + settings.PHOTO_PROOF_PATH+data["photo_proof_img"]
            if send_status !="sent":

                CustomUser.objects.filter(id=customuser.id).delete()

                return Response({
                    "status":"Error",
                    "Message":"Invalid Mobile Number",
                    })
            else:


                return Response({
                    "status":"Success",
                    "Message":"Successfully Registered ",
                    "user":data,
                    
                    })
        else:
            # CustomUser.objects.filter(id=customuser.id).delete()

            print(serializer)
            print(serializer.errors)
            return Response({
                "SignUp":"Denied",
                })



class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    # permission_classes = [permissions.IsAuthenticated,]
    def post(self,request,*args,**kwargs):
        user_type = request.data.pop("user_type")
        # profile_img = request.data.pop("profile_pic")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customuser = serializer.save()
          
            group = Group.objects.get(name=user_type)
            group.user_set.add(customuser)
                        
            otp = ''.join(random.sample("0123456789", 4))
            # if profile_img !="":
            #     pf_name = sav_img(profile_img,customuser.id)
            #     pf_name = settings.BASE_URL+settings.PROFILE_IMAGE_URL+pf_name
            # else:

            #     pf_name = settings.BASE_URL+settings.NO_PROFILE_IMAGE_URL
            message ="sent"
            send_status = "sent"
            random_otp = "0000"
            otp ="0000"
            # message,send_status,random_otp=send_msg_otp_signup_verification(customuser.phone,customuser.name,otp)
            # status = email(customuser.email,customuser.name,otp)
            # print('Email OTP Status: ',status)
            print('OTP Status ')
            print(send_status)
            # save_otp = SendOtp.objects.create(otp_owner=customuser,otp=otp)
            # save_otp.save()
            data = UserSerializer(customuser,context=self.get_serializer_context()).data
            data["user_type"]=user_type
            # data["profile_image"] = pf_name
            if send_status !="sent":

                CustomUser.objects.filter(id=customuser.id).delete()

                return Response({
                    "status":"Error",
                    "Message":"Invalid Mobile Number",
                    })
            else:


                return Response({
                    "status":"Success",
                    "Message":"Successfully Registered and waiting for OTP Verification",
                    "user":data,
                    
                    })
        else:
            print(serializer)
            print(serializer.errors)
            return Response({
                "SignUp":"Denied",
                })



class OtpVerify(APIView):
    # Allow any user (authenticated or not) to access this url 
    permission_classes = [permissions.AllowAny,]
 
    def post(self, request):    
        
        email = ''
        user_id = 0
        token = ""
        otp =""
        if not request.data:
            validation_message = 'Please provide email'
            return JsonResponse({'status': 'error', 'message': validation_message} , safe=False)

        if 'email' in request.data and request.data["email"]=="":
            validation_message = "Please Enter Valid Email"
            return JsonResponse({'status': 'error', 'message': validation_message} , safe=False)

        if 'user_id' in request.data:
            user_id = request.data["user_id"]
        
        if 'otp' in request.data:
            otp = request.data["otp"]


        # email = request.data['email']
        # user_exists = SendOtp.objects.filter(otp_owner_id=user_id, otp=otp)
        user_exists = True
        if user_exists:
            
            temp = user_exists[0].otp_owner
            print(temp)
            user_exists.update(otp_verified=True,otp="")
            _, token = AuthToken.objects.create(temp)
            validation_status = 'Success'
            validation_message = 'Successfully Verified Your email Address'
            CustomUser.objects.filter(id=user_id).update(user_verified = True)
            print(token)
            return JsonResponse({'status': validation_status, 'message': validation_message,"token":token} , safe=False)

        else:
            validation_status = 'Error'
            validation_message = 'Invalid OTP'
            return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)



class ForgotPassword(APIView):
    # Allow any user (authenticated or not) to access this url 
    permission_classes = [permissions.AllowAny,]
 
    def post(self, request):    
        
        validation_status = 'error4'
        validation_message = 'Error4'        
        phone = ''
        data ={}
        user_id = 0
        token = ""
        print(request.data.keys())
        if not request.data:
            validation_message = 'Please provide phone'
            return JsonResponse({'status': 'error', 'message': validation_message} , safe=False)

        if 'phone' in request.data.keys(): 
            if request.data["phone"]=="":
                validation_message = "Please Enter Valid phone"
                return JsonResponse({'status': 'error', 'message': validation_message} , safe=False)

            phone = request.data["phone"]
            print(phone)

            user_exists = CustomUser.objects.filter(phone=phone)
            # print(user_exists[0].phone,"phone number")

            if user_exists:
                validation_status = "Success"
                validation_message = "Otp Send on Registered Phone Number."
                data['id'] = user_exists[0].id
                random_otp ="0000"
                # otp = "".join(random.sample("0123456789", 4))
                # status = forgot_password_email(user_exists[0].email,user_exists[0].name,otp)
                name = user_exists[0].name
                phone = user_exists[0].phone
                # print(name,phone,otp,"*********")
                # message,send_status,random_otp = send_msg_otp_signup_verification(phone, name,otp)
                # print(status)

                otp1 = SendOtp(otp_owner_id=user_exists[0].id,otp=random_otp,otp_verified=False)
                otp1.save()
                print(otp1)

            else:
                validation_status = 'error5'
                validation_message = 'Invalid User5'
        if 'email' in request.data:
            if request.data["email"]=="":
                validation_message = "Please Enter Valid email"
                return JsonResponse({'status': 'error', 'message': validation_message} , safe=False)
            email = request.data["email"]
            print(email)

            user_exists = CustomUser.objects.filter(email__iexact=email)
            if user_exists:
                validation_status = "Success"
                validation_message = "Otp Send on Registered email ."
                data['id'] = user_exists[0].id
                random_otp="0000"
                # status = email(customuser.email,customuser.name,otp)
                # message,send_status,random_otp = send_msg_otp_signup_verification(user_exists[0].name,user_exists[0].phone)
                # print(status)
                otp1 = SendOtp.objects.filter(otp_owner_id=user_exists[0].id).update(otp=random_otp,otp_verified=False)
                print(otp1)
            else:
                validation_status = 'error3'
                validation_message = 'Invalid User3'  


        return JsonResponse({'status': validation_status, 'message': validation_message,"data":data} , safe=False)



class ForgotOtpVerify(APIView):
    # Allow any user (authenticated or not) to access this url 
    permission_classes = [permissions.AllowAny,]
 
    def post(self, request):    
        
        validation_status = 'error'
        validation_message = 'Error'        
        email = ''
        user_id = 0
        data = {}
        if not request.data:
            validation_message = 'Please provide email'
            return JsonResponse({'status': 'error', 'message': validation_message} , safe=False)



        if 'user_id' in request.data:
            user_id = request.data["user_id"]



        try:
            otp = request.data["otp"]
    
            user_exists = SendOtp.objects.filter(otp_owner_id=user_id,otp=otp)
            print(user_exists)

            if user_exists:
                user_exists.update(otp_verified=True,otp="")

          
                validation_status = 'Success'
                validation_message = 'Successfully Verified Your Otp'
                data["id"] =user_id
       

            else:
                validation_status = 'Error'
                validation_message = 'Invalid Otp.'

        except Exception as ex:
            import sys,os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno,"@#@#@#@#")
            print(ex,"#####123232")          
            validation_message = 'Invalid input'
        
        return JsonResponse({'status': validation_status, 'message': validation_message,"data":data} , safe=False)


class ChangeForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny,]
    def post(self, request):
        validation_status = 'error'
        validation_message = 'Error'
        user_id = 0
        user_id = request.data['user_id']
        new_password = request.data['new_password']
        confirm_password = request.data['confirm_password']
        user_exists = CustomUser.objects.filter(id=user_id)
        if user_exists:
            new_password = make_password(new_password)
            user_exists.update(password=new_password)
            print(user_exists[0].password,"@@@@@@@@@@@@@")
            print('\n\n\n\n\nPassword Changed \n\n\n\n')
            return JsonResponse({'status': 'Success', 'message': 'Password Change successfully.'} , safe=False)
        else:
            print('\n\n\n\n\nInvalid user \n\n\n\n')
            return JsonResponse({'status': 'error', 'message': 'User does not exist.'} , safe=False)



def save_img(img,user_id,image_path,img_type):
    # image_path = settings.QUERY_IMAGE_URL
    # print(img)
    file = img["type"].split('.')
    # file_name = file[0]          
    file_ext = file[1]


    save_img_name = str(img_type)+"_"+str(user_id)+"."+str(file_ext)
                    
    imagefile = str(image_path)+str(save_img_name)

    # dt =  img["image"].split(",")
    imgstring = img["image"]
    imgstring = imgstring.split(',')
    print(imgstring,"*********************8")
    print("*********************8")
    import base64
    imgdata = base64.b64decode(imgstring[1])

    with open(imagefile, 'wb+') as f:

        f.write(imgdata)
    return settings.BASE_URL+image_path+save_img_name







# def upload

# def upload_product_image_file(record_id, post_image, image_path, image_tag):
#   image_name = ''
#   image_path = settings.PROOF_OF_OWNERSHIP_PATH
#   image_path = IMAGE_TAG[image_tag]
#   if not os.path.exists(image_path):
#       os.makedirs(image_path)
#   image_name = None

#   if post_image != '' and image_path != '' and image_tag != '' and record_id > 0:
#         file_name = post_image["type"].split('.')
#         file_ext = file_name[1]
#         image_name =image_tag+"_"+str(record_id)+"_image."+str(file_ext)
#         imagefile = str(image_path)+str(image_name)
#         imgstring = post_image["image"]
#         # imgstring = post_image["image"]
#         imgstring = imgstring.split(',')
#         print(imgstring,"*********************8")
#         print("*********************8")
#         import base64
#         imgdata = base64.b64decode(imgstring[1])

#         with open(imagefile, 'wb+') as f:
#         f.write(imgdata)

        
#   return image_name


# def upload


# def upload
IMAGE_TAG = {'AadharCard':settings.AADHAR_IMAGE_PATH,'Declaration':settings.DECLARATION_PATH,
            'License':settings.LICENSE_PATH,'LocationSketch':settings.LOCATION_SKETCH_PATH,
            'ProofOfOwnership':settings.PROOF_OF_OWNERSHIP_PATH,'RevenueApplication':settings.REVENUE_APPLICATION_PATH,
            'RevenueApproval':settings.REVENUE_APPROVAL_PATH,'TreeOwnership':settings.TREE_OWNERSHIP_PATH,
            'Signature':settings.SIGN_PATH,'QRCode' :settings.QRCODE_PATH,'Profile':settings.PROFILE_PATH,
            'PhotoProof':settings.PHOTO_PROOF_PATH

    }


def upload_product_image_file(record_id, post_image, image_path, image_tag):
    image_name = ''
    image_path = settings.PROOF_OF_OWNERSHIP_PATH
    image_path = IMAGE_TAG[image_tag]
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    image_name = None
    if post_image != '' and image_path != '' and image_tag != '' and record_id > 0:
        # try:
        filename = post_image["type"].split('.')
        file_ext = filename[1]
        print("")

        image_name =image_tag+"_"+str(record_id)+"_image."+str(file_ext)
        imagefile = str(image_path)+str(image_name)
        imgstring = post_image["image"]
        imgstring = imgstring.split(',')
        import base64
        imgdata = base64.b64decode(imgstring[1])
        with open(imagefile, 'wb+') as f:
            f.write(imgdata)



    return image_name 


def upload_photo_edit_image_file(record_id, post_image, image_path, image_tag):
    image_name = ''
    #image_path = settings.PROOF_OF_OWNERSHIP_PATH
    image_path = IMAGE_TAG[image_tag]
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    image_name = None
    if post_image != '' and image_path != '' and image_tag != '' and record_id > 0:
        # try:
        filename = post_image["type"].split('.')
        file_ext = filename[1]
        print("")

        image_name =image_tag+"_"+str(record_id)+"_image."+str(file_ext)
        imagefile = str(image_path)+str(image_name)
        imgstring = post_image["image"]
        imgstring = imgstring.split(',')
        import base64
        imgdata = base64.b64decode(imgstring[1])
        with open(imagefile, 'wb+') as f:
            f.write(imgdata)



    return image_name





# def upload_product_image_file(record_id, post_image, image_path, image_tag):
#   image_name = ''
#   image_path = settings.PROOF_OF_OWNERSHIP_PATH
#   image_path = IMAGE_TAG[image_tag]
#   if not os.path.exists(image_path):
#       os.makedirs(image_path)
#   image_name = None
#   # j=random.randint(0,1000)
#   if post_image != '' and image_path != '' and image_tag != '' and record_id > 0:
#       try:
#           filename = post_image["type"].split('.')
#           file_ext = filename[1]
#             print("")
#           # arr_len = len(filearr)

#           # if len(filearr) > 1 :
#           #   file_name = filearr[0]          
#           #   file_ext = filearr[arr_len-1]
#               #----------------------------------------#

#             # image_name =image_tag+"_"+str(record_id)+"_image."+str(file_ext)
#             # imagefile = str(image_path)+str(image_name)
#             # with open(imagefile, 'wb+') as destination:
#             #     print(post_image.chunks(),"---====--",destination)
#             #     for chunk in post_image.chunks():
#             #         print(destination,'----==')
#             #         destination.write(chunk)
#       except Exception as Error:
#           print("----here",Error)
#           pass
            
#   return image_name
class UpdateTimberlog(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):
        application=request.data['app_id']
        log_details=request.data['log_details']
        validation_status = ''
        validation_message = ''
        if log_details!="" or application!="" :
            tlog_exist = Timberlogdetails.objects.filter(appform_id=application)
            if tlog_exist:
                tlog_exist.delete()
            # else:

            try:
                tlog=[]
                 # pass
                for i in log_details:
                    print(i)

                    timber = Timberlogdetails(appform_id=application,species_of_tree=i["species_of_tree"], 
                    length=i["length"], breadth=i["breadth"],volume=i["volume"],latitude=i["latitude"],longitude=i["longitude"])
                    tlog.append(timber)
                Timberlogdetails.objects.bulk_create(tlog)
                validation_status = 'Success'
                validation_message = 'Log Details Updated Successfully.'
            except Exception as e:
                print(e,'Error')
                validation_status = 'Fail'
                validation_message = 'Log Details have not been updated successfully.' 
        else:
            validation_status = 'Fail'
            validation_message = 'Log Details have not been updated successfully.'

           
        print(self.request.user.id)        
        return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)
        # return JsonResponse({'message':'Updated successfully!!!','timber_log':list(timber_log)})




class InsertRecord(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        name = ""
        address = ""
        survey_number = ""
        num_trees_proposed_cut = ""
        village = ""
        taluka = ""
        block = ""
        district = ""
        proof_of_ownership_img = ""
        species_of_tree  = ""
        purpose = ""
        log_details = ""
        revenue_application = ""
        revenue_approval = ""
        declaration = ""
        location_sktech = ""
        tree_ownership_detail = ""
        photo_id_proof = "" 
        photo_id_proof_img = "" 
        destination_details = "" 
        vehicle_reg_no = "" 
        driver_name = "" 
        driver_phone = "" 
        mode_of_transport = "" 
        license_image = "" 
        signature_img = "" 

        validation_status = 'error'
        validation_message = 'Error'
        name=request.data["name"]
        address=request.data["address"]
        survey_no=request.data["survey_no"]
        tree_proposed=request.data["tree_proposed"]
        village=request.data["village"]
        district=request.data["district"]
        block=request.data["block"]
        taluka=request.data["taluka"]
        division=request.data["division"]
        area_range=request.data["area_range"]
        pincode=request.data["pincode"]
        # print(request.FILES)
        ownership_proof_img=request.data["ownership_proof_img"]
        revenue_application_img=request.data["revenue_application_img"]
        revenue_approval_img=request.data["revenue_approval_img"]
        declaration_img=request.data["declaration_img"]
        location_sketch_img=request.data["location_sketch_img"]
        tree_ownership_img=request.data["tree_ownership_img"]
        aadhar_card_img=request.data["aadhar_card_img"]
        signature_img = request.data["signature_img"]
        lic_img=request.data["licence_img"]
        tree_species=request.data["tree_species"]
        purpose = request.data["purpose_cut"]
        veh_reg=request.data["vehicel_reg"]
        driver_name= request.data["driver_name"]
        phone = request.data["phone"]
        mode = request.data["mode"]
        log_details = request.data["log_details"]
        trees_cutted = request.data["trees_cutted"]
        destination_address = request.data["destination_address"]
        print("___________________________")
        url='static/media/'
        application = Applicationform.objects.create(
            name=name,address=address,destination_details=destination_address,
            survey_no=survey_no,village=village,total_trees=tree_proposed,
            district=district,species_of_trees=tree_species,pincode=pincode,
            purpose=purpose,block=block,taluka=taluka,division=division,
            area_range=area_range,by_user=request.user
            )
        print(application)
        saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
        saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
        saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
        saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
        saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
        saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
        saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
        # saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
        saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
        application.proof_of_ownership_of_tree=saved_image_6

                
        image_doc=image_documents.objects.create(app_form=application,
                revenue_approval=saved_image_2,declaration=saved_image_1,
                revenue_application=saved_image_3,location_sktech=saved_image_4,
                tree_ownership_detail=saved_image_5,aadhar_detail=saved_image,
                signature_img=saved_image_8
            )
        application.revenue_approval = True
        application.declaration = True
        uid=request.user.id
        
        application.application_no=generate_app_id(uid,application.id)
 #       application_no=generate_app_id(uid,application.id)
        #clprint(application_no,"*******************")
        application.signature_img = True
        application.revenue_application = True
        application.location_sktech = True
        application.tree_ownership_detail = True
        application.aadhar_detail = True
#        tem = Applicationform.objects.filter(id = application.id).update(application_no=application_no,signature_img = True,revenue_application = True,location_sktech = True,tree_ownership_detail = True,aadhar_detail = True)
        application.trees_cutted = True
        #print(")s",tem)
        tlog =[]
        application.trees_cutted= True

        if log_details!="" : 
            for i in log_details:
                print(i)

                timber = Timberlogdetails(appform=application,species_of_tree=i["species_of_tree"], 
                length=i["length"], breadth=i["breadth"],volume=i["volume"],latitude=i["latitude"],longitude=i["longitude"])
                tlog.append(timber)
            Timberlogdetails.objects.bulk_create(tlog)
        application.save()
        saved_image_7 =""
        if lic_img!="":
            saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')

        vehicle = Vehicle_detials.objects.create(app_form=application,
            license_image=saved_image_7,vehicle_reg_no=veh_reg,
            driver_name=driver_name,driver_phone=phone,
            mode_of_transport=mode
            )
        validation_status = 'Success'
        validation_message = 'Data Saved Successfully.'   
        print(self.request.user.id)        
        return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)



class NewInsertRecord(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        name = ""
        address = ""
        survey_number = ""
        num_trees_proposed_cut = ""
        village = ""
        taluka = ""
        block = ""
        district = ""
        proof_of_ownership_img = ""
        species_of_tree  = ""
        purpose = ""
        log_details = ""
        revenue_application = ""
        revenue_approval = ""
        declaration = ""
        location_sktech = ""
        tree_ownership_detail = ""
        photo_id_proof = "" 
        photo_id_proof_img = "" 
        destination_details = "" 
        vehicle_reg_no = "" 
        driver_name = "" 
        driver_phone = "" 
        mode_of_transport = "" 
        license_image = "" 
        signature_img = "" 

        validation_status = 'error'
        validation_message = 'Error'
        name=request.data["name"]
        address=request.data["address"]
        survey_no=request.data["survey_no"]

        tree_proposed=request.data["tree_proposed"]
        village=request.data["village"]
        district=request.data["district"]
        block=request.data["block"]
        taluka=request.data["taluka"]
        division=request.data["division"]
        area_range=request.data["area_range"]
        pincode=request.data["pincode"]
        # print(request.FILES)
        ownership_proof_img=request.data["ownership_proof_img"]
        revenue_application_img=request.data["revenue_application_img"]
        revenue_approval_img=request.data["revenue_approval_img"]
        declaration_img=request.data["declaration_img"]
        location_sketch_img=request.data["location_sketch_img"]
        tree_ownership_img=request.data["tree_ownership_img"]
        aadhar_card_img=request.data["aadhar_card_img"]
        signature_img = request.data["signature_img"]
        lic_img=request.data["licence_img"]
        tree_species=request.data["tree_species"]
        purpose = request.data["purpose_cut"]
        veh_reg=request.data["vehicel_reg"]
        driver_name= request.data["driver_name"]
        phone = request.data["phone"]
        mode = request.data["mode"]
        log_details = request.data["log_details"]
        trees_cutted = request.data["trees_cutted"]
        destination_address = request.data["destination_address"]
        destination_state = request.data["destination_state"]

        print("___________________________")
        url='static/media/'
        application = Applicationform.objects.create(
            name=name,address=address,destination_details=destination_address,destination_state=destination_state,
            survey_no=survey_no,village=village,total_trees=tree_proposed,
            district=district,species_of_trees=tree_species,pincode=pincode,
            purpose=purpose,block=block,taluka=taluka,division=division,
            area_range=area_range,by_user=request.user
            )
        print(application)
        saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
        saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
        saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
        saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
        saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
        saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
        saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
        # saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
        saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
        application.proof_of_ownership_of_tree=saved_image_6

                
        image_doc=image_documents.objects.create(app_form=application,
                revenue_approval=saved_image_2,declaration=saved_image_1,
                revenue_application=saved_image_3,location_sktech=saved_image_4,
                tree_ownership_detail=saved_image_5,aadhar_detail=saved_image,
                signature_img=saved_image_8
            )
        application.revenue_approval = True
        application.declaration = True
        uid=request.user.id
        if destination_state!="Kerala":
            application.other_state = True
            #application.is_form_two = True

        
        application.application_no=generate_app_id(uid,application.id)
 #       application_no=generate_app_id(uid,application.id)
        #clprint(application_no,"*******************")
        application.signature_img = True
        application.revenue_application = True
        application.location_sktech = True
        application.tree_ownership_detail = True
        application.aadhar_detail = True
#        tem = Applicationform.objects.filter(id = application.id).update(application_no=application_no,signature_img = True,revenue_application = True,location_sktech = True,tree_ownership_detail = True,aadhar_detail = True)
        application.trees_cutted = True
        #print(")s",tem)
        tlog =[]
        application.trees_cutted= True

        if log_details!="" : 
            for i in log_details:
                print(i)

                timber = Timberlogdetails(appform=application,species_of_tree=i["species_of_tree"], 
                length=i["length"], breadth=i["breadth"],volume=i["volume"],latitude=i["latitude"],longitude=i["longitude"])
                tlog.append(timber)
            Timberlogdetails.objects.bulk_create(tlog)
        application.save()
        saved_image_7 =""
        if lic_img!="":
            saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')

        vehicle = Vehicle_detials.objects.create(app_form=application,
            license_image=saved_image_7,vehicle_reg_no=veh_reg,
            driver_name=driver_name,driver_phone=phone,
            mode_of_transport=mode
            )
        validation_status = 'Success'
        validation_message = 'Data Saved Successfully.'   
        print(self.request.user.id)        
        return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)


class ListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        application_detail = list(Applicationform.objects.filter(by_user_id=self.request.user.id,is_noc=False).values().order_by('-id'))
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)
        
class ListRange(APIView):

    permission_classes = [permissions.AllowAny,]
 
    def get(self, request):

        application_detail = list(Range.objects.filter(is_delete=False).values('name'))
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Fetched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)

class LoadDivision(APIView):

    permission_classes = [permissions.AllowAny,]
 
    def post(self, request):
        range_area = request.data['range_area']
        application_detail = list(Range.objects.filter(name__iexact=range_area).values('division_id__name'))
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Fetched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)




class ViewApplication(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        app_id = request.data["app_id"]
        groups=list(request.user.groups.values_list('name',flat = True))
        
        chck_app = Applicationform.objects.filter(id=app_id)
        if chck_app:
            pass
        else:
            validation_status = 'Error'
            validation_message = 'Application Not Found.'   
            return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)

            
            
        application_detail = list(Applicationform.objects.filter(id=app_id).values())
         
        if application_detail[0]["proof_of_ownership_of_tree"]!="":
            application_detail[0].update({"proof_of_ownership_of_tree":settings.SERVER_BASE_URL+settings.PROOF_OF_OWNERSHIP_PATH+application_detail[0]["proof_of_ownership_of_tree"]})
            # print("*12222222222222222222222222222")

        trees_species_list = list(TreeSpecies.objects.all().values('name'))
        # image_document =""
        # print("********************")
                #         "revenue_approval": "RevenueApproval_94_image.png",
                # "declaration": "Declaration_94_image.png",
                # "revenue_application": "RevenueApplication_94_image.png",
                # "location_sktech": "LocationSketch_94_image.png",
                # "tree_ownership_detail": "TreeOwnership_94_image.png",
                # "aadhar_detail": "AadharCard_94_image.png"

        image_document = list(image_documents.objects.filter(app_form_id=app_id).values())
        t1 = image_document[0]["signature_img"]
        image_document[0].update({"signature_img":settings.SERVER_BASE_URL+settings.SIGN_PATH +image_document[0]["signature_img"]})
        image_document[0].update({"declaration":settings.SERVER_BASE_URL+settings.DECLARATION_PATH +image_document[0]["declaration"]})
        image_document[0].update({"revenue_approval":settings.SERVER_BASE_URL+settings.REVENUE_APPROVAL_PATH +image_document[0]["revenue_approval"]})
        image_document[0].update({"location_sktech":settings.SERVER_BASE_URL+settings.LOCATION_SKETCH_PATH +image_document[0]["location_sktech"]})
        image_document[0].update({"tree_ownership_detail":settings.SERVER_BASE_URL+settings.TREE_OWNERSHIP_PATH +image_document[0]["tree_ownership_detail"]})
        image_document[0].update({"aadhar_detail":settings.SERVER_BASE_URL+settings.AADHAR_IMAGE_PATH +image_document[0]["aadhar_detail"]})
        image_document[0].update({"revenue_application":settings.SERVER_BASE_URL+settings.REVENUE_APPLICATION_PATH +image_document[0]["revenue_application"]})



        # if application_detail:
        vehicle = list(Vehicle_detials.objects.filter(app_form_id=app_id).values())
        #print(vehicle[0],"22222222222222222222222")
        isvehicle=''
        if vehicle:
            vehicle=vehicle[0]
            vehicle.update({"license_image":settings.SERVER_BASE_URL+settings.LICENSE_PATH+vehicle["license_image"]})
            # vehicle.update({"photo_of_vehicle_with_number":settings.SERVER_BASE_URL+settings.PHOTO_OF_VEHICLE+vehicle["photo_of_vehicle_with_number"]})

            

        else:
            isvehicle = 'Not Applicable'
        is_timberlog=''
        timber_log = Timberlogdetails.objects.filter(appform_id=app_id)
        if timber_log:
            timber_log=list(timber_log.values())
            # for tl in timber_log:
            #     tl.update({"log_qr_code_img":settings.SERVER_BASE_URL+settings.LOG_QR})
        else:
            timber_log = ""
            is_timberlog='N/A'
        print("********************")

        # transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
        transit_pass_exist = False
        # if groups[0] == "revenue officer" and application_detail[0].verify_office == True:
        #     transit_pass_exist = True
        # elif groups[0] == "deputy range officer" and application_detail[0].depty_range_officer == True:
        #     transit_pass_exist = True
        # elif groups[0] == "forest range officer" and application_detail[0].verify_range_officer == True:
        #     transit_pass_exist = True
        # else:
        #     pass
        print(transit_pass_exist,'----TP')
        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        print(self.request.user.id)
        species_list = Species_geodetails.objects.filter(appform_id=app_id).values_list('species_tree__name',flat=True)
        species_location = Species_geodetails.objects.filter(appform_id=app_id).values('species_tree__name','latitude','longitude')
        data = {
            'applications':application_detail,'image_documents':image_document,'groups':groups,'species_location':list(species_location),
            'transit_pass_exist':transit_pass_exist,'vehicle':vehicle,'timber_log':timber_log,'species_list':list(species_list),
            'trees_species_list':trees_species_list,'isvehicle':isvehicle,'is_timberlog':is_timberlog}
        print(data,"&&&&&&&&&&&&&&&&&&&&&&&&/")
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':data} , safe=False)




def new_transit_pass_pdf(request,applicant_no):
    logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
    logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
    logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
    # image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
    # transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
    # log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
    # signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
    # qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)

    # print(applicant_no,"******************")
    application = Applicationform.objects.filter(id=applicant_no).exclude(transit_pass_id=0)
    # print(application)
    is_vehicle = "NO"
    vdata = {}
    if application:
        import datetime

        if application[0].other_state == False:
            authorizer_name = application[0].approved_by.name if application[0].is_noc==False and application[0].deemed_approval==False else 'N/A' 
        else:
            authorizer_name = application[0].approved_by_division.name if application[0].is_noc==False and application[0].deemed_approval==False else 'N/A'  


        #authorizer_name = application[0].approved_by.name
        application=application.values()

        veh_details = Vehicle_detials.objects.filter(app_form_id = applicant_no)
        if veh_details:
            is_vehicle = "YES"
            vdata = veh_details.values()
        image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
        transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
        log_details = Timberlogdetails.objects.filter(appform_id=applicant_no).values()
        signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
        qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
        date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
        main_url=settings.SERVER_BASE_URL+'static/media/qr_code/'
        # print(application[0]['approved_by_id__name'])\
        # <td style="width :300px !important; text-align: center;font-size: 16px">{{each.species_of_tree}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.length}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.breadth}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.volume}}</td>
        log={}
        # print(log_details.values(),'----')
        for each in log_details:
            each['main_url'] = main_url+each['log_qr_code_img']
            # log['']=
            # log['']=
            # log['']=
            # log['']=

        # print(log_details,'------=')
        expiry_date = date_1 + datetime.timedelta(days=7)
        context = {'application':application,"logo1":logo1,"logo2":logo2,"logo3":logo3,'main_url':main_url,
            'signature_img':signature_img,'qr_img':qr_img,'authorizer_name':authorizer_name,"is_vehicle":is_vehicle,"vdata":vdata
            ,'transitpass':transitpass,'log_details':log_details,'expiry_date':expiry_date}
        from datetime import datetime

        response = HttpResponse(content_type='application/pdf')
        # datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
        # applicant_no.replace('-','')
        today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
        # print(today_stamp,'======',datetime.now())
        filename= 'TransitPass-'+str(application[0]['application_no'])+'-'+today_stamp+''
        response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
        # find the template and render it.
        template = get_template('pdf_template/newtransitpass_tbl.html')
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        return response
    else:
        print('No Data in Summary')
        return JsonResponse({'status': "error", 'message': "Error"} , safe=False)
# return JsonResponse({'status': "error", 'message': "Error"} , safe=False)

# class new_user_report(APIView):
#     permission_classes = [permissions.IsAuthenticated,]
# @api_view(['post'])
# # @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def new_user_report(request,applicant_no):
    logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
    logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
    logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
    # groups=request.user.groups.values_list('name',flat = True)
    # pr/int(groups,"*********************")
    transitpass = TransitPass.objects.filter(app_form_id=applicant_no)
    qr_img=''
    is_transitpass='ok'
    if transitpass:
        transitpass=transitpass[0]
    # log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
    # signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
        qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
    else:
        qr_img = ''
        is_transitpass='Not Generated'
    # config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    # config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    print('-------------------',logo1,logo2,qr_img,'-----=============')
    # pdf = pdfkit.from_string(wt, False,configuration=config)
    template =''
    # if groups[0] in ['revenue officer','deputy range officer','forest range officer']:
    #     template = get_template("pdf_template/report.html")
    # else:
    # template = get_template("pdf_template/userreport.html")
    application = Applicationform.objects.filter(id=applicant_no).values()
    # print(application)
    if application:
        approved_names = Applicationform.objects.filter(id=applicant_no).values('approved_by_division__name','approved_by_deputy__name','approved_by_revenue__name','approved_by__name')
        import datetime
        date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
        expiry_date = date_1 + datetime.timedelta(days=7)
        context = {'application':application,"logo1":logo1,"logo2":logo2,'expiry_date':expiry_date,"logo3":logo3,
        'qr_img':qr_img,'transitpass':transitpass,'is_transitpass':is_transitpass,'approved_names':list(approved_names)}  # data is the context data that is sent to the html file to render the output. 
        response = HttpResponse(content_type='application/pdf')
        from datetime import datetime
        today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
        # print(today_stamp,'======',datetime.now())
        filename= 'UserReport-'+str(application[0]['application_no'])+'-'+today_stamp+''
        response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'

        
        # response['Content-Disposition'] = 'attachment; filename="UserReport.pdf"'
        # print(context)
        # print(context,"#$$$$$$$###########/")
        template = get_template('pdf_template/newreport.html')
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        return response
    else:
        print('No Data in Summary')
        return JsonResponse({'status': "error", 'message': "Error"} , safe=False)

class EditProfile(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        # application_detail = list(Custome.objects.filter(by_user_id=self.request.user.id).values())
        # application_detail = list(Applicationform.objects.filter().values())
        # request.data()
        user_id=request.user.id
        contact = request.data["contact"]
        #email = request.data["email"]
        name = request.data["name"]
        address = request.data["address"]
        profile_photo = None
        user= CustomUser.objects.filter(id=user_id)
        if "profile_photo" in request.data:
          profile_photo =request.data["profile_photo"]
          print(profile_photo,'---pp')
        # print(request.body.profile_photo)
        # print(request.POST)
        # print(contact,'------------')
        
        url = 'media/upload/profile/'
        profile_pic=''
        if CustomUser.objects.filter(phone = contact).exclude(id=user_id).exists():
            validation_status = 'Fail'
            validation_message = 'Contact already exist!'
            return JsonResponse({'status': validation_status, 'message': validation_message})
        if profile_photo is None:
            # profile_pic = upload_product_image_file(user_id,profile_photo,url,'Profile')
            # print(profile_pic,'------')
            user_update= user.update(
                phone = contact,
                name=name,
                address=address,
                # email= email,
                )
            validation_status = 'Success'
            validation_message = 'Profile Updated Successfully!'
        else:
            # saved_photo=upload_product_image_file(customuser.id,photo_proof_img,url,'PhotoProof')
                # customuser.photo_proof_img = saved_photo
            # CustomUser.objects.filter(id=customuser.id).update(photo_proof_img=settings.SERVER_BASE_URL + settings.PHOTO_PROOF_PATH+saved_photo)
            url=''
            profile_pic = upload_photo_edit_image_file(user_id,profile_photo,url,'Profile')
            print(profile_pic,'------')
            user_update= user.update(
                phone = contact,
                name=name,
                address=address,
                profile_pic = profile_pic
                # email= email,
                )
            validation_status = 'Success'
            validation_message = 'Profile Updated Successfully!'   
        return JsonResponse({'status': validation_status, 'message': validation_message})

from django.db.models import Value
from django.db.models.functions import Concat
class ViewProfile(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        # application_detail = list(Custome.objects.filter(by_user_id=self.request.user.id).values())
        # application_detail = list(Applicationform.objects.filter().values())
        # request.data()
        user_id=request.user.id
        
        user_details={}
        photo_url = settings.SERVER_BASE_URL+settings.PROFILE_PATH
        user= CustomUser.objects.filter(id=user_id).values('phone','email','name','address').annotate(pic_url=Concat(Value(photo_url), 'profile_pic'))
        # print(user[0])
        # user_details = 
        validation_status = 'Success'
        # validation_message = 'Profile Successfully!'
        user_data = user[0]   
        return JsonResponse({'status': validation_status,'user':user_data})

class UpdateVehicle(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):
        app_id = request.data['app_id']
        veh_reg=request.data['veh_reg']
        driver_name= request.data['driver_name']
        phone = request.data['phn']
        mode = request.data['mode']
        lic_img=request.data['lic_img']
        application_detail = Applicationform.objects.filter(id=app_id)

        if not application_detail:
            message = "Application does not exist!"
            return JsonResponse(
                    {'message':message,'status':'Fail'})
        vehicle = Vehicle_detials.objects.filter(app_form_id=app_id)
        
        message=''
        # request.POST.get('vehicle_detail')
        url=''
        license_image=''
        if vehicle:
            if lic_img is None:
                # license_image=request.POST.get('lic_img_val')
                vehicle = vehicle.update(
                        vehicle_reg_no=veh_reg,
                        driver_name=driver_name,driver_phone=phone,
                        mode_of_transport=mode
                        )
                message='Vehicles details updated successfully!'
            else:
                url  = 'static/media/upload/license/'
                license_image=upload_photo_edit_image_file(app_id,lic_img,url,'License')
                vehicle = vehicle.update(
                        vehicle_reg_no=veh_reg, license_image=license_image,
                        driver_name=driver_name,driver_phone=phone,
                        mode_of_transport=mode
                        )
                message='Vehicles details updated successfully!'
            # vehicle=vehicle[0]

        # timber_log = Timberlogdetails.objects.filter(appform_id=app_id).values()
        else:
                url  = 'static/media/upload/license/'
                license_image=upload_photo_edit_image_file(app_id,lic_img,url,'License')
        # if is_vehicle == 'yes':
                vehicle = Vehicle_detials.objects.create(app_form_id=app_id,
                    vehicle_reg_no=veh_reg, license_image=license_image,
                    driver_name=driver_name,driver_phone=phone,
                    mode_of_transport=mode
                    )
                message='Vehicles details added successfully!'
        return JsonResponse({'status': 'Success', 'message': message})
        
class UpdateVehicle2(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request,app_id):
        # app_id = request.data['app_id']
        veh_reg=request.data['veh_reg']
        driver_name= request.data['driver_name']
        phone = request.data['phn']
        mode = request.data['mode']
        lic_img=request.data['lic_img']
        #lic_img=''
        #if 'lic_img' not in request.data:
        #    lic_img=None
        #else:
         #   lic_img=request.data['lic_img']

        application_detail = Applicationform.objects.filter(id=app_id)

        if not application_detail:
            message = "Application does not exist!"
            return JsonResponse(
                    {'message':message,'status':'Fail'})
        vehicle = Vehicle_detials.objects.filter(app_form_id=app_id)
        
        message=''
        # request.POST.get('vehicle_detail')
        url=''
        license_image=''
        if vehicle:
            if lic_img is None:
                # license_image=request.POST.get('lic_img_val')
                vehicle = vehicle.update(
                        vehicle_reg_no=veh_reg,
                        driver_name=driver_name,driver_phone=phone,
                        mode_of_transport=mode
                        )
                message='Vehicles details updated successfully!'
                
            else:
                license_image=upload_product_image_file(app_id,lic_img,url,'License')
                vehicle = vehicle.update(
                        vehicle_reg_no=veh_reg, license_image=license_image,
                        driver_name=driver_name,driver_phone=phone,
                        mode_of_transport=mode
                        )
                message='Vehicles details updated successfully!'
            # vehicle=vehicle[0]

        # timber_log = Timberlogdetails.objects.filter(appform_id=app_id).values()
        else:
                license_image=upload_product_image_file(app_id,lic_img,url,'License')
        # if is_vehicle == 'yes':
                vehicle = Vehicle_detials.objects.create(app_form_id=app_id,
                    vehicle_reg_no=veh_reg, license_image=license_image,
                    driver_name=driver_name,driver_phone=phone,
                    mode_of_transport=mode
                    )
                message='Vehicles details added successfully!'
        return JsonResponse({'status': 'Success', 'message': message,'id':app_id})

def summary_report(request):
    # logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
    # logo2 = settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
    logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
    logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
    logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
    # config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    # config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    # pdf = pdfkit.from_string(wt, False,configuration=config)
    template = get_template("pdf_template/newsummaryreport.html")
    # css = os.path.join(settings.STATIC_URL, 'css/summaryreport.css', 'summaryreport.css')
    applications = Applicationform.objects.all().order_by('-id')
    
    if applications:
        context = {'applications':applications,"logo1":logo1,"logo2":logo2,"logo3":logo3}  # data is the context data that is sent to the html file to render the output. 
        html = template.render(context)  # Renders the template with the context data.
        # pdf = pdfkit.from_string(html, False, configuration=config)
        # pdf = open("summaryreport.pdf")
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="Summary Report.pdf"'
        today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
        # print(today_stamp,'======',datetime.now())
        filename= 'SummaryReport-'+today_stamp+''
        response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
        # find the template and render it.
        # template = get_template('pdf_template/transitpass.html')
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
        # pdf.close()
        # os.remove("summaryreport.pdf")  # remove the locally created pdf file.
        return response
    else:
        # message = "No Data Found"
        print('No Data in Summary')
        return HttpResponseRedirect(reverse('officer_dashboard'))

# @login_required
def qr_code_pdf(request,applicant_no):
    # logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
    logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
    
    logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
    logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
    # image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
    # transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
    # log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
    # signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
    # qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)

    print(applicant_no,"******************")
    application = Applicationform.objects.filter(id=applicant_no).exclude(transit_pass_id=0)
    print(application)
    if application:
        authorizer_name = application[0].approved_by.name if application[0].deemed_approval==False else ''
        application=application.values()
        
        transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
        log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
        # signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
        qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
        from datetime import datetime
        date_1 = datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
        main_url = settings.SERVER_BASE_URL+"""static/media/qr_code/"""
        # print(application[0]['approved_by_id__name'])
        # print(main_url,log_details[0].log_qr_code)
        req_url=request.META['HTTP_HOST'] 
        print(req_url,"-----HOST")
        # expiry_date = date_1 + datetime.timedelta(days=7)
        from datetime import timedelta
        expiry_date = date_1 + timedelta(days=7)
        context = {'application':application,"logo1":logo1,"logo2":logo2,"logo3":logo3,"req_url":req_url,'main_url':main_url,
            'transitpass':transitpass,'log_details':log_details}

        response = HttpResponse(content_type='application/pdf')
        today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
        # print(today_stamp,'======',datetime.now())
        filename= 'QRCodes-'+str(application[0]['application_no'])+'-'+today_stamp+''
        response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
        # find the template and render it.
        template = get_template('pdf_template/log_newqrcode.html')
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        if pisa_status.err:
            return JsonResponse({"status":"error","message":"Error"})
        return response
    else:
        print('No Data in Summary')
        return JsonResponse({"status":"error","message":"Error"})



# STATUS_CHOICES = (
#     ('S', _("Submitted")),
#     ('P', _("Pending")),
#     ('A', _("Approved")),
#     ('R', _("Rejected")),
# )
class dashbord_chart(APIView):
    permission_classes = [permissions.IsAuthenticated,]


    def get(self,request):

        tot_app = Applicationform.objects.all().count()
        tot_submitted = Applicationform.objects.filter(application_status="S").count()
        tot_approved = Applicationform.objects.filter(application_status="A").count()
        tot_pending = Applicationform.objects.filter(application_status="P").count()
        tot_rejected = Applicationform.objects.filter(application_status="R").count()

        per_submitted = tot_submitted*100/tot_app

        per_approved = tot_approved*100/tot_app
        per_pending = tot_pending*100/tot_app
        per_rejected = tot_rejected*100/tot_app

        data={}
        print(tot_app,tot_approved,tot_pending,tot_rejected,tot_submitted)
        data["tot_application"] = tot_app


        data["tot_submitted"] = tot_submitted
        data["tot_approved"] = tot_approved
        data["tot_pending"] = tot_pending
        data["tot_rejected"] = tot_rejected


        data["per_submitted"] = per_submitted

        data["per_approved"] = per_approved
        data["per_pending"] = per_pending
        data["per_rejected"] = per_rejected


        validation_status = 'Success'
        validation_message = 'Data Fetched Successfully.'
        print(self.request.user.id)        
        return JsonResponse({'status': validation_status, 'message': validation_message,"data":data} , safe=False)




class dashbord_AppList(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    def get(self,request):

        applist= list(Applicationform.objects.all().values())

        validation_status = 'Success'
        validation_message = 'Data Fetched Successfully.'
        return JsonResponse({'status': validation_status, 'message': validation_message,"data":applist} , safe=False)

def random_generate_number(size, chars=string.ascii_uppercase + string.digits): 
    return ''.join(random.choice(chars) for x in range(size))

def get_qr_code(app_id):
	stringdata = '1234567890ABCDEFGHIJKLMNPSTUVWXYZ'	
	generate_number = 'SA'+str(app_id)+random_generate_number(12, stringdata)  
	code_exist = TransitPass.objects.filter(qr_code__iexact=generate_number)
	if code_exist:
		generate_number = get_qr_code()	 
	return generate_number

def generate_qrcode_image(qrcode_string, qrcode_path, record_id):
	
	image_name = 'QR_'+str(qrcode_string)+'_PR_'+str(record_id)+'.png'
	#image_path = settings.QRCODE_PATH
	image_path = qrcode_path
	image_file = str(image_path)+str(image_name)

	try:
	
		qr = qrcode.QRCode(border=4)
		qrcode_string = settings.SERVER_BASE_URL+'app/scanqr/'+qrcode_string
		qr.add_data(qrcode_string)
		qr.make(fit=True)
		#img = qr.make_image(fill_color="red", back_color="#23dda0")
		img = qr.make_image()
		img.save(image_file)
	except Exception as error:
		print(error,"-")
		image_name = ''
	
	return image_name

def get_log_qr_code(app_id,log_id):
	stringdata = '1234567890ABCDEFGHIJKLMNPSTUVWXYZ'	
	generate_number = 'TLOG'+str(app_id)+'_'+random_generate_number(12, stringdata)+'_'+str(log_id)  
	code_exist = Timberlogdetails.objects.filter(log_qr_code__iexact=generate_number)
	if code_exist:
		generate_number = get_log_qr_code(app_id,log_id)	 
	return generate_number

def generate_log_qrcode_image(qrcode_string, qrcode_path, record_id,log_data):
	
	image_name = 'QR_'+str(qrcode_string)+'.png'
	#image_path = settings.QRCODE_PATH
	image_path = qrcode_path
	image_file = str(image_path)+str(image_name)

	try:
	
		qr = qrcode.QRCode(border=4)
		# log_data={}
		# 				log_data['parent_tp_app_no']=application_detail[0].application_no
		# 				log_data['destination_details']=application_detail[0].destination_details
		# 				log_data['species']=each_timber['species_of_tree']
		# 				log_data['latitude']=each_timber['latitude']
		# 				log_data['longitude']=each_timber['longitude']
		# 				log_data['length']=each_timber['length']
		# 				log_data['breadth']=each_timber['breadth']
		# 				log_data['volume']=each_timber['volume']
		# 				log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
		qrcode_string = settings.SERVER_BASE_URL+'app/scan_logqr/'+qrcode_string
		# qrcode_string = log_data
		qr.add_data(qrcode_string)
		qr.make(fit=True)
		#img = qr.make_image(fill_color="red", back_color="#23dda0")
		img = qr.make_image()
		img.save(image_file)
	except Exception as error:
		print(error,"-")
		image_name = ''
	
	return image_name


# @login_required
# @group_required('revenue officer','deputy range officer','forest range officer')
class approve_transit_pass(APIView):
    permission_classes = [permissions.IsAuthenticated,]


    def post(self,request):
        app_id = request.data["app_id"]
        application_detail = Applicationform.objects.filter(id=app_id)
        groups=request.user.groups.values_list('name',flat = True)
        reason = request.data["reason"]
        if application_detail:
            if application_detail[0].application_status=='R':
                return JsonResponse({'message':'Action cannot be taken, Once Application rejected!'})
        else:
            return JsonResponse({'message':'Bad Request!'})
        if request.data["type"] == 'REJECT':
            print(reason,'--reason')

            if groups[0] == "revenue officer":
                application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                disapproved_by=request.user.id,disapproved_by_grp="By Revenue Officer",
                    application_status='R',verify_office = True,verify_office_date = date.today())
            elif groups[0] == "deputy range officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].verify_office==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
                            application_status='R',depty_range_officer = True,deputy_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Revenue Officer Action is Pending !'})
                # pass
            elif groups[0] == "forest range officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].depty_range_officer==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Forest Officer",
                        application_status='R',verify_range_officer = True,range_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Deputy Officer Action is Pending !'})
                # pass
            else:
                pass
            return JsonResponse({'message':'Application has been disapproved!'})
            # return render(request,"my_app/tigram/application_details.html",{'applicant':APPLICATION,'applications':application_detail,'message':'Application has been disapproved!'})

        vehicle_detail = Vehicle_detials.objects.filter(app_form_id=app_id)
        # transit_pass = TransitPass.object.filter(app_form_id=app_id)
        if application_detail :

            reason=request.data['reason']
            if groups[0] == "revenue officer":
                application_detail.update(
                reason_office = reason ,
                application_status = 'P',
                approved_by_revenue = request.user,
                verify_office = True,
                verify_office_date = date.today(),
                # transit_pass_id=transit_pass.id,
                # transit_pass_created_date = datetime.date.today(),
                )
            elif groups[0] == "deputy range officer":
                if application_detail[0].verify_office==True:
                    application_detail.update(
                    reason_depty_ranger_office = reason ,
                    application_status = 'P',
                    approved_by_deputy = request.user,
                    depty_range_officer = True,
                    deputy_officer_date = date.today(),
                    # transit_pass_id=transit_pass.id,
                    # transit_pass_created_date = datetime.date.today(),
                    )
                else:
                    JsonResponse({'message':'Application cannot be approved as Revenue Officer Approval is Pending !'})
            # if vehicle_detail:
            elif groups[0] == "forest range officer":
                if application_detail[0].depty_range_officer==True:
                    qr_code=get_qr_code(app_id)
                    print(qr_code,'-----QR')
                    qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
                    print(qr_img,'----qr_path')
                    is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
                    if is_timber:
                        for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
                            log_qr_code=get_log_qr_code(app_id,each_timber['id'])
                            print(log_qr_code,'-----LOG QR')

                            log_data='Log Details:\n'
                            log_data+='Application No. :-'+application_detail[0].application_no+'\n'
                            log_data+='Destination :-'+application_detail[0].destination_details+'\n'
                            log_data+='Species Name :-'+each_timber['species_of_tree']+'\n'
                            log_data+='Length :-'+str(each_timber['length'])+'\n'
                            log_data+='Girth :-'+str(each_timber['breadth'])+'\n'
                            log_data+='Volume :-'+str(each_timber['volume'])+'\n'
                            log_data+='Latitude :-'+str(each_timber['latitude'])+'\n'
                            log_data+='Longitude :-'+str(each_timber['longitude'])+'\n'
                            log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
                            print(log_qr_img,'----qr_path')
                            is_timber.filter(id=each_timber['id']).update(log_qr_code=log_qr_code,log_qr_code_img=log_qr_img)

                    if vehicle_detail:
                        # vehicle=vehicle_detail[0]
                        transit_pass=TransitPass.objects.create(
                            vehicle_reg_no=vehicle_detail[0].vehicle_reg_no,
                            driver_name = vehicle_detail[0].driver_name,
                            driver_phone = vehicle_detail[0].driver_phone,
                            mode_of_transport = vehicle_detail[0].mode_of_transport,
                            license_image = vehicle_detail[0].license_image,
                            photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
                            state = application_detail[0].state,
                            district = application_detail[0].district,
                            taluka = application_detail[0].taluka,
                            block = application_detail[0].block,
                            village = application_detail[0].village,
                            qr_code = qr_code,
                            qr_code_img =qr_img, 
                            app_form_id = app_id
                        )
                    else:
                        transit_pass=TransitPass.objects.create(
                            state = application_detail[0].state,
                            district = application_detail[0].district,
                            taluka = application_detail[0].taluka,
                            block = application_detail[0].block,
                            village = application_detail[0].village,
                            qr_code = qr_code,
                            qr_code_img =qr_img, 
                            app_form_id = app_id
                        )
                    application_detail.update(
                        reason_range_officer = reason ,
                        application_status = 'A',
                        approved_by = request.user,
                        verify_range_officer = True,
                        range_officer_date = date.today(),
                        transit_pass_id=transit_pass.id,
                        transit_pass_created_date = date.today(),
                        )
                else:
                    JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
                # application_detail[0].save()
                
            else:
                pass
        return JsonResponse({'message':'Application has been approved!'})
"""

class approve_transit_pass(APIView):
    permission_classes = [permissions.IsAuthenticated,]


    def post(self,request):
        app_id = request.data["app_id"]
        application_detail = Applicationform.objects.filter(id=app_id)
        groups=request.user.groups.values_list('name',flat = True)
        reason = request.data["reason"]
        if application_detail:
            if application_detail[0].application_status=='R':
                return JsonResponse({'message':'Action cannot be taken, Once Application rejected!'})
        else:
            return JsonResponse({'message':'Bad Request!'})
        if request.data["type"] == 'REJECT':
            print(reason,'--reason')

            if groups[0] == "revenue officer":
                application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                disapproved_by=request.user.id,disapproved_by_grp="By Revenue Officer",
                    application_status='R',verify_office = True,verify_office_date = date.today())
            elif groups[0] == "deputy range officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].verify_office==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
                            application_status='R',depty_range_officer = True,deputy_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Revenue Officer Action is Pending !'})
                # pass
            elif groups[0] == "forest range officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].depty_range_officer==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Forest Officer",
                    application_status='R',verify_range_officer = True,range_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Deputy Officer Action is Pending !'})

                # pass


            elif groups[0] == "division officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].verify_range_officer==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Division Officer",
                    application_status='R',division_officer = True,division_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Forest Range Officer Action is Pending !'})
                # pass
            else:
                pass
            return JsonResponse({'message':'Application has been disapproved!'})
            # return render(request,"my_app/tigram/application_details.html",{'applicant':APPLICATION,'applications':application_detail,'message':'Application has been disapproved!'})

        vehicle_detail = Vehicle_detials.objects.filter(app_form_id=app_id)
        # transit_pass = TransitPass.object.filter(app_form_id=app_id)
        if application_detail :

            reason=request.data['reason']
            if groups[0] == "revenue officer":
                application_detail.update(
                reason_office = reason ,
                application_status = 'P',
                approved_by_revenue = request.user,
                verify_office = True,
                verify_office_date = date.today(),
                # transit_pass_id=transit_pass.id,
                # transit_pass_created_date = datetime.date.today(),
                )
            elif groups[0] == "deputy range officer":
                if application_detail[0].verify_office==True:
                    application_detail.update(
                    reason_depty_ranger_office = reason ,
                    application_status = 'P',
                    approved_by_deputy = request.user,
                    depty_range_officer = True,
                    deputy_officer_date = date.today(),
                    # transit_pass_id=transit_pass.id,
                    # transit_pass_created_date = datetime.date.today(),
                    )
                else:
                    JsonResponse({'message':'Application cannot be approved as Revenue Officer Approval is Pending !'})
            # if vehicle_detail:
            elif groups[0] == "forest range officer":

                if application_detail[0].depty_range_officer==True:
                    if application_detail[0].other_state == False:
                        qr_code=get_qr_code(app_id)
                        print(qr_code,'-----QR')
                        qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
                        print(qr_img,'----qr_path')
                        is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
                        if is_timber:
                            for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
                                log_qr_code=get_log_qr_code(app_id,each_timber['id'])
                                print(log_qr_code,'-----LOG QR')

                                log_data='Log Details:\n'
                                log_data+='Application No. :-'+application_detail[0].application_no+'\n'
                                log_data+='Destination :-'+application_detail[0].destination_details+'\n'
                                log_data+='Species Name :-'+each_timber['species_of_tree']+'\n'
                                log_data+='Length :-'+str(each_timber['length'])+'\n'
                                log_data+='Girth :-'+str(each_timber['breadth'])+'\n'
                                log_data+='Volume :-'+str(each_timber['volume'])+'\n'
                                log_data+='Latitude :-'+str(each_timber['latitude'])+'\n'
                                log_data+='Longitude :-'+str(each_timber['longitude'])+'\n'
                                log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
                                print(log_qr_img,'----qr_path')
                                is_timber.filter(id=each_timber['id']).update(log_qr_code=log_qr_code,log_qr_code_img=log_qr_img)

                        if vehicle_detail:
                            # vehicle=vehicle_detail[0]
                            transit_pass=TransitPass.objects.create(
                                vehicle_reg_no=vehicle_detail[0].vehicle_reg_no,
                                driver_name = vehicle_detail[0].driver_name,
                                driver_phone = vehicle_detail[0].driver_phone,
                                mode_of_transport = vehicle_detail[0].mode_of_transport,
                                license_image = vehicle_detail[0].license_image,
                                photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        else:
                            transit_pass=TransitPass.objects.create(
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        application_detail.update(
                            reason_range_officer = reason ,
                            application_status = 'A',
                            approved_by = request.user,
                            verify_range_officer = True,
                            range_officer_date = date.today(),
                            transit_pass_id=transit_pass.id,
                            transit_pass_created_date = date.today(),
                            )
                    else:
                        application_detail.update(
                        reason_range_officer = reason ,
                        application_status = 'P',
                        approved_by = request.user,
                        verify_range_officer = True,
                        range_officer_date = date.today(),
                        )
					# JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
			# application_detail[0].save()
                else:
                    JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
            elif groups[0] == "division officer":
                if application_detail[0].verify_range_officer==True:
                    if application_detail[0].other_state == True:
                        qr_code=get_qr_code(app_id)
                        print(qr_code,'-----QR')
                        qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
                        print(qr_img,'----qr_path')
                        is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
                        if is_timber:
                            for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
                                log_qr_code=get_log_qr_code(app_id,each_timber['id'])
                                print(log_qr_code,'-----LOG QR')

                                log_data='Log Details:\n'
                                log_data+='Application No. :-'+application_detail[0].application_no+'\n'
                                log_data+='Destination :-'+application_detail[0].destination_details+'\n'
                                log_data+='Species Name :-'+each_timber['species_of_tree']+'\n'
                                log_data+='Length :-'+str(each_timber['length'])+'\n'
                                log_data+='Girth :-'+str(each_timber['breadth'])+'\n'
                                log_data+='Volume :-'+str(each_timber['volume'])+'\n'
                                log_data+='Latitude :-'+str(each_timber['latitude'])+'\n'
                                log_data+='Longitude :-'+str(each_timber['longitude'])+'\n'
                                log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
                                print(log_qr_img,'----qr_path')
                                is_timber.filter(id=each_timber['id']).update(log_qr_code=log_qr_code,log_qr_code_img=log_qr_img)

                        if vehicle_detail:
                            # vehicle=vehicle_detail[0]
                            transit_pass=TransitPass.objects.create(
                                vehicle_reg_no=vehicle_detail[0].vehicle_reg_no,
                                driver_name = vehicle_detail[0].driver_name,
                                driver_phone = vehicle_detail[0].driver_phone,
                                mode_of_transport = vehicle_detail[0].mode_of_transport,
                                license_image = vehicle_detail[0].license_image,
                                photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        else:
                            transit_pass=TransitPass.objects.create(
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        application_detail.update(
                            reason_division_officer = reason ,
                            application_status = 'A',
                            approved_by_division = request.user,
                            division_officer = True,
                            division_officer_date = date.today(),
                            transit_pass_id=transit_pass.id,
                            transit_pass_created_date = date.today(),
                            )
                    else:
                        JsonResponse({'message':'Application cannot be approved !'})
                        # JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
                # application_detail[0].save()
                else:
                    JsonResponse({'message':'Application cannot be approved as Forest Range Officer Approval is Pending !'})
            else:
                pass
        return JsonResponse({'message':'Application has been approved!'})
"""









# class changeApp_status(APIView):
#   permission_classes = [permissions.IsAuthenticated,]
#   def post(self,request):

#         # app_id = request.data["app_id"]
#         # app_status = request.data["app_status"]
#         # app_reason = request.data["app_reason"]

#         application_detail = Applicationform.objects.filter(id=app_id)
#         groups=request.user.groups.values_list('name',flat = True)
#         reason = request.POST.get('reason')
#         if application_detail:
#             if application_detail[0].application_status=='R':
#                 return JsonResponse({'message':'Action cannot be taken, Once Application rejected!'})
#         else:
#             return JsonResponse({'message':'Bad Request!'})
#         if request.POST.get('type') == 'REJECT':
#             print(reason,'--reason')

#             if groups[0] == "revenue officer":
#                 application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
#                     application_status='R',verify_office = True,verify_office_date = date.today())
#             elif groups[0] == "deputy range officer":
#                 # application_detail = Applicationform.objects.filter(id=app_id)
#                 if application_detail[0].verify_office==True:
#                     application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
#                             application_status='R',depty_range_officer = True,deputy_officer_date = date.today())
#                 else:
#                     JsonResponse({'message':'Application cannot be disapproved as Revenue Officer Action is Pending !'})
#                 # pass
#             elif groups[0] == "forest range officer":
#                 # application_detail = Applicationform.objects.filter(id=app_id)
#                 if application_detail[0].depty_range_officer==True:
#                     application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
#                         application_status='R',verify_range_officer = True,range_officer_date = date.today())
#                 else:
#                     JsonResponse({'message':'Application cannot be disapproved as Deputy Officer Action is Pending !'})
#                 # pass
#             else:
#                 pass
#             return JsonResponse({'message':'Application has been disapproved!'})
#             # return render(request,"my_app/tigram/application_details.html",{'applicant':APPLICATION,'applications':application_detail,'message':'Application has been disapproved!'})

#         vehicle_detail = Vehicle_detials.objects.filter(app_form_id=app_id)
#         # transit_pass = TransitPass.object.filter(app_form_id=app_id)
#         if application_detail :

#             reason=request.POST.get('reason')
#             if groups[0] == "revenue officer":
#                 application_detail.update(
#                 reason_office = reason ,
#                 application_status = 'P',
#                 approved_by = request.user,
#                 verify_office = True,
#                 verify_office_date = date.today(),
#                 # transit_pass_id=transit_pass.id,
#                 # transit_pass_created_date = datetime.date.today(),
#                 )
#             elif groups[0] == "deputy range officer":
#                 if application_detail[0].verify_office==True:
#                     application_detail.update(
#                     reason_depty_ranger_office = reason ,
#                     application_status = 'P',
#                     approved_by = request.user,
#                     depty_range_officer = True,
#                     deputy_officer_date = date.today(),
#                     # transit_pass_id=transit_pass.id,
#                     # transit_pass_created_date = datetime.date.today(),
#                     )
#                 else:
#                     JsonResponse({'message':'Application cannot be approved as Revenue Officer Approval is Pending !'})
#             # if vehicle_detail:
#             elif groups[0] == "forest range officer":
#                 if application_detail[0].depty_range_officer==True:
#                     qr_code=get_qr_code(app_id)
#                     print(qr_code,'-----QR')
#                     qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
#                     print(qr_img,'----qr_path')
#                     is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
#                     if is_timber:
#                         for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
#                             log_qr_code=get_log_qr_code(app_id,each_timber['id'])
#                             print(log_qr_code,'-----LOG QR')

#                             log_data='Log Details:\n'
#                             log_data+='Application No. :-'+application_detail[0].application_no+'\n'
#                             log_data+='Destination :-'+application_detail[0].destination_details+'\n'
#                             log_data+='Species Name :-'+each_timber['species_of_tree']+'\n'
#                             log_data+='Length :-'+str(each_timber['length'])+'\n'
#                             log_data+='Girth :-'+str(each_timber['breadth'])+'\n'
#                             log_data+='Volume :-'+str(each_timber['volume'])+'\n'
#                             log_data+='Latitude :-'+str(each_timber['latitude'])+'\n'
#                             log_data+='Longitude :-'+str(each_timber['longitude'])+'\n'
#                             log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
#                             print(log_qr_img,'----qr_path')
#                             is_timber.filter(id=each_timber['id']).update(log_qr_code=log_qr_code,log_qr_code_img=log_qr_img)

#                     if vehicle_detail:
#                         # vehicle=vehicle_detail[0]
#                         transit_pass=TransitPass.objects.create(
#                             vehicle_reg_no=vehicle_detail[0].vehicle_reg_no,
#                             driver_name = vehicle_detail[0].driver_name,
#                             driver_phone = vehicle_detail[0].driver_phone,
#                             mode_of_transport = vehicle_detail[0].mode_of_transport,
#                             license_image = vehicle_detail[0].license_image,
#                             photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
#                             state = application_detail[0].state,
#                             district = application_detail[0].district,
#                             taluka = application_detail[0].taluka,
#                             block = application_detail[0].block,
#                             village = application_detail[0].village,
#                             qr_code = qr_code,
#                             qr_code_img =qr_img, 
#                             app_form_id = app_id
#                         )
#                     else:
#                         transit_pass=TransitPass.objects.create(
#                             state = application_detail[0].state,
#                             district = application_detail[0].district,
#                             taluka = application_detail[0].taluka,
#                             block = application_detail[0].block,
#                             village = application_detail[0].village,
#                             qr_code = qr_code,
#                             qr_code_img =qr_img, 
#                             app_form_id = app_id
#                         )
#                     application_detail.update(
#                         reason_range_officer = reason ,
#                         application_status = 'A',
#                         approved_by = request.user,
#                         verify_range_officer = True,
#                         range_officer_date = date.today(),
#                         transit_pass_id=transit_pass.id,
#                         transit_pass_created_date = date.today(),
#                         )
#                 else:
#                     JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
#                 # application_detail[0].save()
                
#             else:
#                 pass
#         return JsonResponse({'message':'Application has been approved!'})




class ApprovedListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        groups=request.user.groups.values_list('name',flat = True)
        officer_range=''
        # if groups[0] =='revenue officer':
        #     officer_range=RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
        # else:
        #     officer_range=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)

        
        # if officer_range !='':

        #         application_detail = list(Applicationform.objects.filter(area_range=officer_range[0].range_name.name,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))
        # else:
        #         application_detail = list(Applicationform.objects.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))
        if groups[0] =='revenue officer':
            officer_range=RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
            if officer_range !='':
                application_detail = list(Applicationform.objects.filter(verify_office=True,area_range=officer_range[0].range_name.name,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))
            else:
                application_detail = list(Applicationform.objects.filter(verify_office=True,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))


            
        elif groups[0] =='deputy range officer':
            officer_range=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
            if officer_range !='':
                application_detail = list(Applicationform.objects.filter(depty_range_officer=True,area_range=officer_range[0].range_name.name,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))
            else:
                application_detail = list(Applicationform.objects.filter(depty_range_officer=True,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))

        elif groups[0] =='forest range officer':
            officer_range=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
            if officer_range !='':
                # application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(Q(verify_office=False)|Q(application_status='R'),verify_office=False,area_range=officer_range[0].range_name.name,is_noc=False).values().order_by('-id'))
                application_detail = list(Applicationform.objects.filter(verify_range_officer=True,area_range=officer_range[0].range_name.name,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))

            else:
                application_detail = list(Applicationform.objects.filter(verify_range_officer=True,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).values().order_by('-id'))


       # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)




class DfoApprovedListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            application_detail = list(Applicationform.objects.filter(verify_office=True,area_range__iexact =area_range,division__iexact = div[0]["division_name__name"],deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')).values().order_by('-id'))
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            application_detail = list(Applicationform.objects.filter(verify_office=True,area_range__iexact =area_range,division__iexact = div[0]["division_name__name"],deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')).values().order_by('-id'))


       # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)


class sfdApprovedListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            application_detail = list(Applicationform.objects.filter(verify_office=True,area_range__iexact =area_range,division__iexact = division,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')).values().order_by('-id'))
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            application_detail = list(Applicationform.objects.filter(verify_office=True,area_range__iexact =area_range,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')).values().order_by('-id'))
        
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            application_detail = list(Applicationform.objects.filter(verify_office=True,division__iexact = division,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')).values().order_by('-id'))



        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            application_detail = list(Applicationform.objects.filter(verify_office=True,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')).values().order_by('-id'))


       # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)





class PendingListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        groups=request.user.groups.values_list('name',flat = True)
        officer_range=''
        if groups[0] =='revenue officer':
            officer_range=RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
            if officer_range !='':
                application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,area_range=officer_range[0].range_name.name,is_noc=False).values().order_by('-id'))
            else:
                application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,is_noc=False).values().order_by('-id'))


            
        elif groups[0] =='deputy range officer':
            officer_range=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
            if officer_range !='':
                application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(depty_range_officer=False,area_range=officer_range[0].range_name.name,is_noc=False).values().order_by('-id'))
            else:
                application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(depty_range_officer=False,is_noc=False).values().order_by('-id'))

        elif groups[0] =='forest range officer':
            officer_range=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
            if officer_range !='':
                # application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(Q(verify_office=False)|Q(application_status='R'),verify_office=False,area_range=officer_range[0].range_name.name,is_noc=False).values().order_by('-id'))
                application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_range_officer=False,area_range=officer_range[0].range_name.name,is_noc=False).values().order_by('-id'))

            else:
                application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_range_officer=False,is_noc=False).values().order_by('-id'))

        
        # application_detail = list(Applicationform.objects.filter().values())
        #import date
        #print(application_detail[0]["tp_expiry_date"],"*****************")

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)



class sfdPendingListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):
        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,area_range=area_range,division=division,is_noc=False).values().order_by('-id'))
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,area_range=area_range,division=division,is_noc=False).values().order_by('-id'))
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,area_range=area_range,is_noc=False).values().order_by('-id'))
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,division=division,is_noc=False).values().order_by('-id'))
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,is_noc=False).values().order_by('-id'))


        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)





class DfoPendingListViewApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(area_range__iexact =area_range,division__iexact = div[0]["division_name__name"],is_noc=False).values().order_by('-id'))
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            application_detail = list(Applicationform.objects.exclude(Q(application_status='A')|Q(application_status='R')).filter(division__iexact = div[0]["division_name__name"],is_noc=False).values().order_by('-id'))


        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)










class table_one(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        ty = list(Applicationform.objects.filter(is_noc=False).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))


        return Response(ty, status=status.HTTP_200_OK)

class dfo_table_one(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        print(request.user)
        area_range = request.data["area_range"]
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            ty = list(Applicationform.objects.filter(is_noc=False,area_range__iexact =area_range,division__iexact = div[0]["division_name__name"]).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))


        else:

            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            ty = list(Applicationform.objects.filter(is_noc=False,division__iexact = div[0]["division_name__name"]).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))


        return Response(ty, status=status.HTTP_200_OK)



class sfd_table_one(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        print(request.user)
        division = request.data["division"]
        area_range = request.data["area_range"]
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            ty = list(Applicationform.objects.filter(is_noc=False,area_range__iexact =area_range,division_iexact=division).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))

        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            ty = list(Applicationform.objects.filter(is_noc=False,area_range__iexact =area_range,division_iexact=division).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))

        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            ty = list(Applicationform.objects.filter(is_noc=False,division_iexact=division).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))

        else:

            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            ty = list(Applicationform.objects.filter(is_noc=False).values('created_date').annotate(no_of_received=Count('pk')).annotate(no_of_approved=Count(Case(When(application_status='A',then=F('id')),output_field=IntegerField(),))).annotate(no_of_rejected=Count(Case(When(application_status='R',then=F('id')),output_field=IntegerField(),))).order_by('created_date'))


        return Response(ty, status=status.HTTP_200_OK)




class table_two(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        
        app_list = Applicationform.objects.filter(application_status='R',is_noc=False).values('disapproved_reason')
   
        len_aplist = len(app_list)
        dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disapproved_reason')) }

        return Response(dict_of_percentages, status=status.HTTP_200_OK)


class dfo_table_two(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Applicationform.objects.filter(application_status='R',is_noc=False,area_range__iexact=area_range,division__iexact = div[0]["division_name__name"]).values('disapproved_reason')
    
            len_aplist = len(app_list)
            dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disapproved_reason')) }

        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Applicationform.objects.filter(application_status='R',is_noc=False,division__iexact = div[0]["division_name__name"]).values('disapproved_reason')
    
            len_aplist = len(app_list)
            dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disappr oved_reason')) }

        return Response(dict_of_percentages, status=status.HTTP_200_OK)


class sfd_table_two(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        division = request.data["division"]
        area_range = request.data["area_range"]
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='R',is_noc=False,area_range__iexact =area_range,division_iexact=division).values('disapproved_reason')
    
            len_aplist = len(app_list)
            dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disapproved_reason')) }
            
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='R',is_noc=False,area_range__iexact =area_range).values('disapproved_reason')
    
            len_aplist = len(app_list)
            dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disapproved_reason')) }
            
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='R',is_noc=False,division_iexact=division).values('disapproved_reason')
    
            len_aplist = len(app_list)
            dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disapproved_reason')) }

        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='R',is_noc=False).values('disapproved_reason')
    
            len_aplist = len(app_list)
            dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist for reject_type in app_list.annotate(Count('disapproved_reason')) }

        return Response(dict_of_percentages, status=status.HTTP_200_OK)



class table_three(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        applications_list=Timberlogdetails.objects.filter(appform__is_noc=False)
        app_list_ty=applications_list.values('species_of_tree',
        'appform__created_date').annotate(
         no_of_trees=Count('species_of_tree')   
        ).annotate(
         total_no_of_trees=Count('id')  
        ).annotate(
        volume_sum=Sum('volume')
        )
        len_aplist = len(applications_list)
        applications_list_ty = Applicationform.objects.filter(is_noc=False).values('created_date').order_by('created_date').annotate(
            as_float=Cast('total_trees', FloatField())
            ).annotate(
            total_trees=Sum('as_float'),
            )

        context = {}
        context["tabel"]=app_list_ty
        context["graph"] = applications_list_ty
        return Response(context, status=status.HTTP_200_OK)


class dfo_table_three(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            applications_list=Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            app_list_ty=applications_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            total_no_of_trees=Count('id')  
            ).annotate(
            volume_sum=Sum('volume')
            )
            len_aplist = len(applications_list)
            applications_list_ty = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range,division__iexact = div[0]["division_name__name"]).values('created_date').order_by('created_date').annotate(
                as_float=Cast('total_trees', FloatField())
                ).annotate(
                total_trees=Sum('as_float'),
                )


        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)

            applications_list=Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = div[0]["division_name__name"])
            app_list_ty=applications_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            total_no_of_trees=Count('id')  
            ).annotate(
            volume_sum=Sum('volume')
            )
            len_aplist = len(applications_list)
            applications_list_ty = Applicationform.objects.filter(is_noc=False,division__iexact = div[0]["division_name__name"]).values('created_date').order_by('created_date').annotate(
                as_float=Cast('total_trees', FloatField())
                ).annotate(
                total_trees=Sum('as_float'),
                )

        context = {}
        context["tabel"]=app_list_ty
        context["graph"] = applications_list_ty
        return Response(context, status=status.HTTP_200_OK)


class sfd_table_three(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        division = request.data["division"]
        area_range = request.data["area_range"]
        if area_range !=""and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            applications_list=Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = division)
            app_list_ty=applications_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            total_no_of_trees=Count('id')  
            ).annotate(
            volume_sum=Sum('volume')
            )
            len_aplist = len(applications_list)
            applications_list_ty = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range,division__iexact = division).values('created_date').order_by('created_date').annotate(
                as_float=Cast('total_trees', FloatField())
                ).annotate(
                total_trees=Sum('as_float'),
                )
        elif area_range !="" and division=="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            applications_list=Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range)
            app_list_ty=applications_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            total_no_of_trees=Count('id')  
            ).annotate(
            volume_sum=Sum('volume')
            )
            len_aplist = len(applications_list)
            applications_list_ty = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range,appform__state__iexact = div[0]["state_name"]).values('created_date').order_by('created_date').annotate(
                as_float=Cast('total_trees', FloatField())
                ).annotate(
                total_trees=Sum('as_float'),
                )

        elif area_range =="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            applications_list=Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = division)
            app_list_ty=applications_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            total_no_of_trees=Count('id')  
            ).annotate(
            volume_sum=Sum('volume')
            )
            len_aplist = len(applications_list)
            applications_list_ty = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range,division__iexact = div[0]["division_name__name"]).values('created_date').order_by('created_date').annotate(
                as_float=Cast('total_trees', FloatField())
                ).annotate(
                total_trees=Sum('as_float'),
                )

        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            applications_list=Timberlogdetails.objects.filter(appform__is_noc=False)
            app_list_ty=applications_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            total_no_of_trees=Count('id')  
            ).annotate(
            volume_sum=Sum('volume')
            )
            len_aplist = len(applications_list)
            applications_list_ty = Applicationform.objects.filter(is_noc=False).values('created_date').order_by('created_date').annotate(
                as_float=Cast('total_trees', FloatField())
                ).annotate(
                total_trees=Sum('as_float'),
                )

        context = {}
        context["tabel"]=app_list_ty
        context["graph"] = applications_list_ty
        return Response(context, status=status.HTTP_200_OK)















class table_four(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
        totalvolume=app_list.aggregate(Sum('volume'))
        print(totalvolume,'-----xxxxxxxxx---------')
        app_list=app_list.values('appform__destination_details',
        'appform__created_date').annotate(
        volume_sum=Sum('volume')
        ).annotate(
        volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
        # output_field=format('volume_percentage', ".2f"),
        ).order_by('appform__created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)




class dfo_table_four(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = div[0]["division_name__name"])
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)

            
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class sfd_table_four(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        division = request.data["division"]
        area_range = request.data["area_range"]
        context={}
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = division)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = division)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)

            
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)





class table_five(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
        app_list=app_list.values('species_of_tree','appform__destination_details',
        'appform__created_date').annotate(
         no_of_trees=Count('species_of_tree')   
        ).annotate(
        volume_sum=Sum('volume')
        ).order_by('appform__created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class dfo_table_five(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = div[0]["division_name__name"])
            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class sfd_table_five(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        division = request.data["division"]
        area_range = request.data["area_range"]
        context={}
        if area_range !="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = division)
            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        elif area_range =="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = division)
            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
            
        elif area_range !="" and division=="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range)
            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
            no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class table_six(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
        totalvolume=app_list.aggregate(Sum('volume'))
        print(totalvolume,'-----xxxxxxxxx---------')
        app_list=app_list.values('appform__destination_details',
        'appform__created_date').annotate(
        volume_sum=Sum('volume')
        ).annotate(
        volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
        # output_field=format('volume_percentage', ".2f"),
        ).order_by('appform__created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)




class dfo_table_six(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = div[0]["division_name__name"])
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)




class dfo_table_six(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = div[0]["division_name__name"])
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class sfd_table_six(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division !="" :
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact=division)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
            
            
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact=division)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
            totalvolume=app_list.aggregate(Sum('volume'))
            print(totalvolume,'-----xxxxxxxxx---------')
            app_list=app_list.values('appform__destination_details',
            'appform__created_date').annotate(
            volume_sum=Sum('volume')
            ).annotate(
            volume_percentage=(F('volume_sum')/totalvolume['volume__sum'])*100,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)




class table_seven(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Applicationform.objects.filter(application_status='A',is_noc=False)
        totalapp=app_list.count()
        print(totalapp,'-----xxxxxxxxx---------')
        app_list=app_list.values(
        'created_date').annotate(
        no_of_applicantions=Count('id')
        ).annotate(
        applications_percentage=F('no_of_applicantions')*100/totalapp,
        # output_field=format('volume_percentage', ".2f"),
        ).annotate(
        time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
        # output_field=time_taken_applications.strftime('%j'),
        ).order_by('created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class dfo_table_seven(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Applicationform.objects.filter(application_status='A',is_noc=False,area_range__iexact=area_range,division__iexact = div[0]["division_name__name"])
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
            # output_field=time_taken_applications.strftime('%j'),
            ).order_by('created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Applicationform.objects.filter(application_status='A',is_noc=False,division__iexact = div[0]["division_name__name"])
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
            # output_field=time_taken_applications.strftime('%j'),
            ).order_by('created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class sfd_table_seven(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='A',is_noc=False,area_range__iexact=area_range,division__iexact = division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
            # output_field=time_taken_applications.strftime('%j'),
            ).order_by('created_date')
            len_aplist = len(app_list)
            
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='A',is_noc=False,area_range__iexact=area_range)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
            # output_field=time_taken_applications.strftime('%j'),
            ).order_by('created_date')
            len_aplist = len(app_list)
            
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='A',is_noc=False,division__iexact = division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
            # output_field=time_taken_applications.strftime('%j'),
            ).order_by('created_date')
            len_aplist = len(app_list)
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(application_status='A',is_noc=False,area_range__iexact=area_range,division__iexact = division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            time_taken_applications=ExtractDay(F('transit_pass_created_date')-F('created_date')),
            # output_field=time_taken_applications.strftime('%j'),
            ).order_by('created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class table_eight(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Applicationform.objects.filter(is_noc=False)
        totalapp=app_list.count()
        print(totalapp,'-----xxxxxxxxx---------')
        app_list=app_list.values(
        'created_date','purpose').annotate(
        no_of_applicantions=Count('id')
        ).annotate(
        applications_percentage=F('no_of_applicantions')*100/totalapp,
        # output_field=format('volume_percentage', ".2f"),
        ).order_by('created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class dfo_table_eight(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range,division__iexact = div[0]["division_name__name"])
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date','purpose').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)
            app_list = Applicationform.objects.filter(is_noc=False,division__iexact = div[0]["division_name__name"])
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date','purpose').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('created_date')
            len_aplist = len(app_list)
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class sfd_table_eight(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self,request):
        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range,division__iexact = division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date','purpose').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('created_date')
            len_aplist = len(app_list)
            
        elif area_range !="" and division=="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(is_noc=False,area_range__iexact=area_range)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date','purpose').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('created_date')
            len_aplist = len(app_list)
            
        elif area_range =="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(is_noc=False,division__iexact=division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date','purpose').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('created_date')
            len_aplist = len(app_list)
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)
            app_list = Applicationform.objects.filter(is_noc=False)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values(
            'created_date','purpose').annotate(
            no_of_applicantions=Count('id')
            ).annotate(
            applications_percentage=F('no_of_applicantions')*100/totalapp,
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('created_date')
            len_aplist = len(app_list)
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class table_nine(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
        totalapp=app_list.count()
        print(totalapp,'-----xxxxxxxxx---------')
        app_list=app_list.values('species_of_tree',
        'appform__created_date').annotate(
        no_of_applicantions=Count('appform__id')
        ).annotate(
        no_after_cutting=Count(Case(
        When(appform__trees_cutted=True,then=F('appform__id')),
        output_field=IntegerField(),)),
        ).annotate(
        no_before_cutting=Count(Case(
        When(appform__trees_cutted=False,then=F('appform__id')),
        output_field=IntegerField(),)),
        ).annotate(
        after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
        # output_field=format('volume_percentage', ".2f"),
        ).annotate(
        before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
        # output_field=format('volume_percentage', ".2f"),
        ).order_by('appform__created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)

        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class dfo_table_nine(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_applicantions=Count('appform__id')
            ).annotate(
            no_after_cutting=Count(Case(
            When(appform__trees_cutted=True,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            no_before_cutting=Count(Case(
            When(appform__trees_cutted=False,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_applicantions=Count('appform__id')
            ).annotate(
            no_after_cutting=Count(Case(
            When(appform__trees_cutted=True,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            no_before_cutting=Count(Case(
            When(appform__trees_cutted=False,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        context['applicantions']=list(app_list)

        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class sfd_table_nine(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range,appform__division__iexact = division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_applicantions=Count('appform__id')
            ).annotate(
            no_after_cutting=Count(Case(
            When(appform__trees_cutted=True,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            no_before_cutting=Count(Case(
            When(appform__trees_cutted=False,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        elif area_range !="" and division =="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__area_range__iexact=area_range)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_applicantions=Count('appform__id')
            ).annotate(
            no_after_cutting=Count(Case(
            When(appform__trees_cutted=True,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            no_before_cutting=Count(Case(
            When(appform__trees_cutted=False,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        elif area_range =="" and division !="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=False,appform__division__iexact = division)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_applicantions=Count('appform__id')
            ).annotate(
            no_after_cutting=Count(Case(
            When(appform__trees_cutted=True,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            no_before_cutting=Count(Case(
            When(appform__trees_cutted=False,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)




        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
            totalapp=app_list.count()
            print(totalapp,'-----xxxxxxxxx---------')
            app_list=app_list.values('species_of_tree',
            'appform__created_date').annotate(
            no_of_applicantions=Count('appform__id')
            ).annotate(
            no_after_cutting=Count(Case(
            When(appform__trees_cutted=True,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            no_before_cutting=Count(Case(
            When(appform__trees_cutted=False,then=F('appform__id')),
            output_field=IntegerField(),)),
            ).annotate(
            after_cutting_percentage=F('no_after_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).annotate(
            before_cutting_percentage=F('no_before_cutting')*100/F('no_of_applicantions'),
            # output_field=format('volume_percentage', ".2f"),
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        context['applicantions']=list(app_list)

        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)





#noc Reports

class table_noc_one(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # ty=list(request.user.groups.all().values('name'))
        # gname=ty[0]["name"]
        # print(gname)
        # gname = Group
        context={}
        app_list = Timberlogdetails.objects.filter(appform__is_noc=True)
        app_list=app_list.values('species_of_tree','appform__destination_details',
        'appform__created_date').annotate(
         no_of_trees=Count('species_of_tree')   
        ).annotate(
        volume_sum=Sum('volume')
        ).order_by('appform__created_date')
        len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)


class dfo_table_noc_one(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        area_range = request.data["area_range"]
        context={}
        if area_range !="":
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=True,appform__area_range__iexact=area_range,appform__division__iexact = div[0]["division_name__name"])

            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
                no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = DivisionOfficerdetail.objects.filter(div_user_id = request.user.id).values('id','division_name__name','division_name__id')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=True,appform__division__iexact = div[0]["division_name__name"])

            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
                no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class sfd_table_noc_one(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        area_range = request.data["area_range"]
        division = request.data["division"]
        context={}
        if area_range !="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=True,appform__area_range__iexact=area_range,appform__division__iexact = division)

            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
                no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
            
        elif area_range !="" and division=="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=True,appform__area_range__iexact=area_range)

            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
                no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
            
        elif area_range =="" and division!="":
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=True,appform__division__iexact = division)

            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
                no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        else:
            div = StateOfficerdetail.objects.filter(state_user_id = request.user.id).values('id','state_name')
            print(div)

            app_list = Timberlogdetails.objects.filter(appform__is_noc=True)

            app_list=app_list.values('species_of_tree','appform__destination_details',
            'appform__created_date').annotate(
                no_of_trees=Count('species_of_tree')   
            ).annotate(
            volume_sum=Sum('volume')
            ).order_by('appform__created_date')
            len_aplist = len(app_list)
        
        context['applicantions']=list(app_list)
        # context['group'] = list(groups)
        print(context,'--=context')
        return JsonResponse(context,safe=False)



class Apply_for_noc(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        name = ""
        address = ""
        survey_number = ""
        num_trees_proposed_cut = ""
        village = ""
        taluka = ""
        block = ""
        district = ""
        proof_of_ownership_img = ""
        species_of_tree  = ""
        purpose = ""
        log_details = []
        revenue_application = ""
        revenue_approval = ""
        declaration = ""
        location_sktech = ""
        tree_ownership_detail = ""
        photo_id_proof = "" 
        photo_id_proof_img = "" 
        destination_details = "" 
        vehicle_reg_no = "" 
        driver_name = "" 
        driver_phone = "" 
        mode_of_transport = "" 
        license_image = "" 
        signature_img = "" 

        validation_status = 'error'
        validation_message = 'Error'
        name=request.data["name"]
        address=request.data["address"]
        survey_no=request.data["survey_no"]
        tree_proposed=request.data["tree_proposed"]
        village=request.data["village"]
        district=request.data["district"]
        block=request.data["block"]
        taluka=request.data["taluka"]
        division=request.data["division"]
        area_range=request.data["area_range"]
        pincode=request.data["pincode"]
        # print(request.FILES)
        # ownership_proof_img=request.data["ownership_proof_img"]
        # revenue_application_img=request.data["revenue_application_img"]
        # revenue_approval_img=request.data["revenue_approval_img"]
        # declaration_img=request.data["declaration_img"]
        # location_sketch_img=request.data["location_sketch_img"]
        # tree_ownership_img=request.data["tree_ownership_img"]
        aadhar_card_img=request.data["aadhar_card_img"]
        signature_img = request.data["signature_img"]
        # lic_img=request.data["licence_img"]
        tree_species=request.data["tree_species"]
        purpose = request.data["purpose_cut"]
        veh_reg=request.data["vehicel_reg"]
        driver_name= request.data["driver_name"]
        phone = request.data["phone"]
        mode = request.data["mode"]
        log_details = request.data["log_details"]
        trees_cutted = request.data["trees_cutted"]
        destination_address = request.data["destination_address"]
        print("___________________________")
        url='static/media/'
        application = Applicationform.objects.create(is_noc=True,
            name=name,address=address,destination_details=destination_address,
            survey_no=survey_no,village=village,total_trees=tree_proposed,
            district=district,species_of_trees=tree_species,pincode=pincode,
            purpose=purpose,block=block,taluka=taluka,division=division,
            area_range=area_range,by_user=request.user
            )
        print(application)
        saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
        # saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
        # saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
        # saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
        # saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
        # saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
        # saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
        # # saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
        saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
        # application.proof_of_ownership_of_tree=saved_image_6

                
        image_doc=image_documents.objects.create(app_form=application,aadhar_detail=saved_image,
                signature_img=saved_image_8
            )
        # application.revenue_approval = True
        # application.declaration = True
        uid=request.user.id
        
        application.application_no=generate_noc_app_id(uid,application.id)
 #       application_no=generate_app_id(uid,application.id)
        #clprint(application_no,"*******************")
        application.signature_img = True
        # application.revenue_application = True
        # application.location_sktech = True
        # application.tree_ownership_detail = True
        application.aadhar_detail = True
        tem = Applicationform.objects.filter(id = application.id).update(application_no=application.id)
        qr_code=get_qr_code(application.id)
        print(qr_code,'-----QR')
        qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, application.id)
        print(qr_img,'----qr_path')
# veh_reg=request.data["vehicel_reg"]
#         driver_name= request.data["driver_name"]
#         phone = request.data["phone"]
#         mode = request.data["mode"]


        transit_pass=TransitPass.objects.create(state = application.state,district = application.district,taluka = application.taluka,block = application.block,village = application.village,qr_code = qr_code,qr_code_img =qr_img,app_form_id = application.id
                            ,vehicle_reg_no=veh_reg,
                            driver_name = driver_name,
                            driver_phone = phone,
                            mode_of_transport = mode)
                            # license_image = vehicle_detail[0].license_image,
                            # photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
        print(transit_pass.id,"&&&&&&&&&&&&&&&&************8")
        # up_det = Applicationform.objects.filter(id = application.id).update(transit_pass_id = transit_pass.id)
        # application.trees_cutted = True
        #print(")s",tem)
        tlog =[]
        application.trees_cutted= True
        application.transit_pass_id = transit_pass.id

        if log_details!="" : 
            for i in log_details:
                print(i)

                timber = Timberlogdetails(appform=application,species_of_tree=i["species_of_tree"], 
                length=i["length"], breadth=i["breadth"],volume=i["volume"],latitude=i["latitude"],longitude=i["longitude"])
                tlog.append(timber)
            Timberlogdetails.objects.bulk_create(tlog)
        application.save()
        # if lic_img!="":
        #     saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')

        vehicle = Vehicle_detials.objects.create(app_form=application,
            vehicle_reg_no=veh_reg,
            driver_name=driver_name,driver_phone=phone,
            mode_of_transport=mode
            )

            #     vehicle = Vehicle_detials.objects.create(app_form=application,
            # license_image=saved_image_7,vehicle_reg_no=veh_reg,
            # driver_name=driver_name,driver_phone=phone,
            # mode_of_transport=mode
            # )
        validation_status = 'Success'
        validation_message = 'Data Saved Successfully.'   
        print(self.request.user.id)        
        return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)



class NocListApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        application_detail = list(Applicationform.objects.filter(is_noc=True).values().order_by('-id'))
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)


class UserNocListApplication(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        application_detail = list(Applicationform.objects.filter(is_noc=True,by_user_id=self.request.user.id).values().order_by('-id'))
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)


def new_noc_pdf(request,applicant_no):
    logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
    logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
    logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
    # image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
    # transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
    # log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
    # signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
    # qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)

    # print(applicant_no,"******************")
    application = Applicationform.objects.filter(id=applicant_no)
    # print(application)
    if application:
        import datetime

        # authorizer_name = application[0].approved_by.name
        application=application.values()
        image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
        transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
        log_details = Timberlogdetails.objects.filter(appform_id=applicant_no).values()
        signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
        qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
        date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
        main_url=settings.SERVER_BASE_URL+'static/media/qr_code/'
        # print(application[0]['approved_by_id__name'])\
        # <td style="width :300px !important; text-align: center;font-size: 16px">{{each.species_of_tree}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.length}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.breadth}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.volume}}</td>
        log={}
        # print(log_details.values(),'----')
        # for each in log_details:
        #     each['main_url'] = main_url+each['log_qr_code_img']
            # log['']=
            # log['']=
            # log['']=
            # log['']=

        # print(log_details,'------=')
        expiry_date = date_1 + datetime.timedelta(days=7)
        context = {'application':application,"logo1":logo1,"logo2":logo2,"logo3":logo3,'main_url':main_url,
            'qr_img':qr_img,'log_details':log_details,'signature_img':signature_img,
            'transitpass':transitpass,'expiry_date':expiry_date}
        from datetime import datetime

        response = HttpResponse(content_type='application/pdf')
        # datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
        # applicant_no.replace('-','')
        today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
        # print(today_stamp,'======',datetime.now())
        filename= 'NOC-'+str(application[0]['application_no'])+'-'+today_stamp+''
        response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
        # find the template and render it.
        template = get_template('pdf_template/noc.html')
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        return response
    else:
        print('No Data in Summary')
        return JsonResponse({'status': "error", 'message': "Error"} , safe=False)


class NocViewApplication(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        app_id = request.data["app_id"]
        groups=list(request.user.groups.values_list('name',flat = True))
        
        chck_app = Applicationform.objects.filter(id=app_id,is_noc=True)
        if chck_app:
            pass
        else:
            validation_status = 'Error'
            validation_message = 'Application Not Found.'   
            return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)

            
            
        application_detail = list(Applicationform.objects.filter(id=app_id).values())
         
        # if application_detail[0]["proof_of_ownership_of_tree"]!="":
        #     application_detail[0].update({"proof_of_ownership_of_tree":settings.SERVER_BASE_URL+settings.PROOF_OF_OWNERSHIP_PATH+application_detail[0]["proof_of_ownership_of_tree"]})
            # print("*12222222222222222222222222222")

        # trees_species_list = list(TreeSpecies.objects.all().values('name'))
        # image_document =""
        # print("********************")
                #         "revenue_approval": "RevenueApproval_94_image.png",
                # "declaration": "Declaration_94_image.png",
                # "revenue_application": "RevenueApplication_94_image.png",
                # "location_sktech": "LocationSketch_94_image.png",
                # "tree_ownership_detail": "TreeOwnership_94_image.png",
                # "aadhar_detail": "AadharCard_94_image.png"

        image_document = list(image_documents.objects.filter(app_form_id=app_id).values())
        t1 = image_document[0]["signature_img"]
        image_document[0].update({"signature_img":settings.SERVER_BASE_URL+settings.SIGN_PATH +image_document[0]["signature_img"]})
        # image_document[0].update({"declaration":settings.SERVER_BASE_URL+settings.DECLARATION_PATH +image_document[0]["declaration"]})
        # image_document[0].update({"revenue_approval":settings.SERVER_BASE_URL+settings.REVENUE_APPROVAL_PATH +image_document[0]["revenue_approval"]})
        # image_document[0].update({"location_sktech":settings.SERVER_BASE_URL+settings.LOCATION_SKETCH_PATH +image_document[0]["location_sktech"]})
        # image_document[0].update({"tree_ownership_detail":settings.SERVER_BASE_URL+settings.TREE_OWNERSHIP_PATH +image_document[0]["tree_ownership_detail"]})
        image_document[0].update({"aadhar_detail":settings.SERVER_BASE_URL+settings.AADHAR_IMAGE_PATH +image_document[0]["aadhar_detail"]})
        # image_document[0].update({"revenue_application":settings.SERVER_BASE_URL+settings.REVENUE_APPLICATION_PATH +image_document[0]["revenue_application"]})



        # if application_detail:
        vehicle = list(Vehicle_detials.objects.filter(app_form_id=app_id).values())
        #print(vehicle[0],"22222222222222222222222")
        isvehicle=''
        if vehicle:
            print("$$$$$$$$$$$")
        #     vehicle=vehicle[0]
        #     vehicle.update({"license_image":settings.SERVER_BASE_URL+settings.LICENSE_PATH+vehicle["license_image"]})
            # vehicle.update({"photo_of_vehicle_with_number":settings.SERVER_BASE_URL+settings.PHOTO_OF_VEHICLE+vehicle["photo_of_vehicle_with_number"]})

            

        else:
            isvehicle = 'Not Applicable'
        is_timberlog=''
        timber_log = Timberlogdetails.objects.filter(appform_id=app_id)
        if timber_log:
            timber_log=list(timber_log.values())
            # for tl in timber_log:
            #     tl.update({"log_qr_code_img":settings.SERVER_BASE_URL+settings.LOG_QR})
        else:
            timber_log = ""
            is_timberlog='N/A'
        print("********************")

        # transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
        transit_pass_exist = False
        # if groups[0] == "revenue officer" and application_detail[0].verify_office == True:
        #     transit_pass_exist = True
        # elif groups[0] == "deputy range officer" and application_detail[0].depty_range_officer == True:
        #     transit_pass_exist = True
        # elif groups[0] == "forest range officer" and application_detail[0].verify_range_officer == True:
        #     transit_pass_exist = True
        # else:
        #     pass
        print(transit_pass_exist,'----TP')
        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        print(self.request.user.id)
        data = {
            'applications':application_detail,'image_documents':image_document,
            'vehicle':vehicle,'timber_log':timber_log,
            'isvehicle':isvehicle,'is_timberlog':is_timberlog}
        print(data,"&&&&&&&&&&&&&&&&&&&&&&&&/")
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':data} , safe=False)



class DeemedApprovedList(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def get(self, request):

        application_detail = list(Applicationform.objects.filter(deemed_approval=True).values().order_by('-id'))
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)
        
        

class GetLocationDataNew(APIView):
    # user = self.request.user.id
    permission_classes = [permissions.AllowAny,]

    def get(self,request):
        temp = []

        dist = District.objects.all()
        taluka = Taluka.objects.all()
        village = Village.objects.all()

        for i in dist:
            dst = {}
            mc = []
            clst1 = []
            tclst1 = []
            mc2 = {}
            dst["district_name"] = i.district_name
            m1 = taluka.filter(dist_id = i.id)
            # c1 = council.filter(dist_id=i.id)
            # t1 = tal.filter(dist_id=i.id)
            # if m1:
            for j in m1:
                mc1 = {}
                mc1["taluka_name"]  = j.taluka_name
                m2 = village.filter(taluka_id = j.id)
                if m2:
                    wlst = []
                    for i in m2:
                        wlst.append(i.village_name)
                    mc1["village_name"]  = wlst
                mc.append(mc1)
                dst["taluka"] = mc
            temp.append(dst)
        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':temp} , safe=False)




#Form Two

class Formtwophaseone(APIView):
    # Allow any user (authenticated or not) to access this url 
    # authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):

        spec_details = ""
        validation_status = 'error'
        validation_message = 'Error'
        name=request.data["name"]
        address=request.data["address"]
        survey_no=request.data["survey_no"]
        species_of_trees=request.data["tree_species"]

        tree_proposed=request.data["tree_proposed"]
        village=request.data["village"]
        district=request.data["district"]
        block=request.data["block"]
        taluka=request.data["taluka"]
        division=request.data["division"]
        area_range=request.data["area_range"]
        pincode=request.data["pincode"]
        spec_geo = request.data["spec_details"]
        # print(request.FILES)
        ownership_proof_img=request.data["ownership_proof_img"]
        revenue_application_img=request.data["revenue_application_img"]
        revenue_approval_img=request.data["revenue_approval_img"]
        declaration_img=request.data["declaration_img"]
        location_sketch_img=request.data["location_sketch_img"]
        tree_ownership_img=request.data["tree_ownership_img"]
        aadhar_card_img=request.data["aadhar_card_img"]
        signature_img = request.data["signature_img"]
        lic_img=request.data["licence_img"]
        # tree_species=request.data["tree_species"]
        purpose = request.data["purpose_cut"]
        veh_reg=request.data["vehicel_reg"]
        driver_name= request.data["driver_name"]
        phone = request.data["phone"]
        mode = request.data["mode"]
        # log_details = request.data["log_details"]
        # trees_cutted = request.data["trees_cutted"]
        destination_address = request.data["destination_address"]
        destination_state = request.data["destination_state"]

        print("___________________________")
        url='static/media/'
        application = Applicationform.objects.create(is_form_two=True,
            name=name,address=address,destination_details=destination_address,destination_state=destination_state,
            survey_no=survey_no,village=village,total_trees=tree_proposed,
            district=district,pincode=pincode,species_of_trees=species_of_trees,
            purpose=purpose,block=block,taluka=taluka,division=division,appsecond_one_date = date.today(),
            area_range=area_range,by_user=request.user)
        print(application)
        saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
        saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
        saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
        saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
        saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
        saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
        saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
        # saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
        saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
        application.proof_of_ownership_of_tree=saved_image_6

                
        image_doc=image_documents.objects.create(app_form=application,
                revenue_approval=saved_image_2,declaration=saved_image_1,
                revenue_application=saved_image_3,location_sktech=saved_image_4,
                tree_ownership_detail=saved_image_5,aadhar_detail=saved_image,
                signature_img=saved_image_8
            )
        application.revenue_approval = True
        application.declaration = True
        uid=request.user.id
        if destination_state!="Kerala":
            application.other_state = True
            # application.is_form_two = True

        
        application.application_no=generate_app_id(uid,application.id)
 #       application_no=generate_app_id(uid,application.id)
        #clprint(application_no,"*******************")
        application.signature_img = True
        application.revenue_application = True
        application.location_sktech = True
        application.tree_ownership_detail = True
        application.aadhar_detail = True
        application.save()
        saved_image_7 =""
        if lic_img!="":
            saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')

#        tem = Applicationform.objects.filter(id = application.id).update(application_no=application_no,signature_img = True,revenue_application = True,location_sktech = True,tree_ownership_detail = True,aadhar_detail = True)
        # application.trees_cutted = True
        #print(")s",tem)
        tlog =[]
        # application.trees_cutted= True
        print(type(spec_geo))
        if spec_geo!="":
            for k in range(len(spec_geo)):

                print(spec_geo[k]["latitude"],"88888888")
                print(spec_geo[k]["longitude"],"(((((((((((((((((")
                #print(application,int(spec_geo[k]["species_of_tree"]))
                lat = spec_geo[k]["latitude"]
                lng= spec_geo[k]["longitude"]
                #spec_id = int(spec_geo[k]["species_of_tree"])
                spec_id = int(spec_geo[k]["Id"])
                spec = Species_geodetails(latitude=lat,longitude=lng,appform=application,species_tree_id=spec_id)
                tlog.append(spec)
                # tlog.append(Species_geodetails(latitude=lat,longitude=lng,appform_id=application.id,species_tree_id=spec_id))
            print(tlog)
        Species_geodetails.objects.bulk_create(tlog)

        # if log_details!="" : 
        #     for i in log_details:
        #         print(i)

        #         timber = Timberlogdetails(appform=application,species_of_tree=i["species_of_tree"], 
        #         length=i["length"], breadth=i["breadth"],volume=i["volume"],latitude=i["latitude"],longitude=i["longitude"])
        #         tlog.append(timber)
        #     Timberlogdetails.objects.bulk_create(tlog)

        vehicle = Vehicle_detials.objects.create(app_form=application,
            license_image=saved_image_7,vehicle_reg_no=veh_reg,
            driver_name=driver_name,driver_phone=phone,
            mode_of_transport=mode
            )
        validation_status = 'Success'
        validation_message = 'Data Saved Successfully.'   
        print(self.request.user.id)        
        return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)




class PhaseTwoFormtwo(APIView):

    permission_classes = [permissions.IsAuthenticated,]
 
    def post(self, request):
        app_id = request.data["app_id"]
        veh_reg=request.data["vehicel_reg"]
        driver_name= request.data["driver_name"]
        phone = request.data["phone"]
        mode = request.data["mode"]
        vehicle_detail = request.data["vehicle_detail"]
        log_details = request.data["log_details"]
        lic_img = request.data["lic_img"]
        trees_cutted = request.data["trees_cutted"]


        phasetwo = Applicationform.objects.update(log_updated_by_user=True,trees_cutted=trees_cutted,appsecond_two_date=date.today())
        tlog = []
        if log_details!="" : 
            for i in log_details:
                print(i)

                timber = Timberlogdetails(appform_id=app_id,species_of_tree=i["species_of_tree"], 
                length=i["length"], breadth=i["breadth"],volume=i["volume"],latitude=i["latitude"],longitude=i["longitude"])
                tlog.append(timber)
            Timberlogdetails.objects.bulk_create(tlog)

        if vehicle_detail == True:

            chk_veh = Vehicle_detials.objects.filter(app_form_id=app_id)
            if chk_veh:
                saved_image_7 =""
                if lic_img!="":
                    saved_image_7=upload_product_image_file(app_id,lic_img,url,'License')

                Vehicle_detials.objects.filter(app_form_id=app_id).update(
                license_image=saved_image_7,vehicle_reg_no=veh_reg,
                driver_name=driver_name,driver_phone=phone,
                mode_of_transport=mode
                )

            else:
                saved_image_7 =""
                if lic_img!="":
                    saved_image_7=upload_product_image_file(app_id,lic_img,url,'License')
                vehicle = Vehicle_detials.objects.create(app_form_id=app_id,
                    license_image=saved_image_7,vehicle_reg_no=veh_reg,
                    driver_name=driver_name,driver_phone=phone,
                    mode_of_transport=mode
                    )


        

        validation_status = 'Success'
        validation_message = 'Form Two Data Submitted.'   
        return JsonResponse({'status': validation_status, 'message': validation_message} , safe=False)







class new_approve_transit_pass(APIView):
    permission_classes = [permissions.IsAuthenticated,]


    def post(self,request):
        app_id = request.data["app_id"]
        application_detail = Applicationform.objects.filter(id=app_id)
        groups=request.user.groups.values_list('name',flat = True)
        reason = request.data["reason"]
        if application_detail:
            if application_detail[0].application_status=='R':
                return JsonResponse({'message':'Action cannot be taken, Once Application rejected!'})
        else:
            return JsonResponse({'message':'Bad Request!'})
        if request.data["type"] == 'REJECT':
            print(reason,'--reason')

            if groups[0] == "revenue officer":
                application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                disapproved_by=request.user.id,disapproved_by_grp="By Revenue Officer",
                    application_status='R',verify_office = True,verify_office_date = date.today())
            elif groups[0] == "deputy range officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].verify_office==True:
                    if application_detail[0].is_form_two ==False:
                        application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                        disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
                                application_status='R',depty_range_officer = True,deputy_officer_date = date.today())
                    else:
                        if application_detail[0].verify_deputy2 == True:
                            application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                            disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
                            application_status='R',verify_deputy2 = True,deputy2_date = date.today())
                        else:
                            print("from Heree@@@@@@@@@@@@@@@")
                            application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                            disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
                            application_status='R',depty_range_officer = True,deputy_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Revenue Officer Action is Pending !'})
                # pass
            elif groups[0] == "forest range officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].depty_range_officer==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Forest Officer",
                    application_status='R',verify_range_officer = True,range_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Deputy Officer Action is Pending !'})

                # pass


            elif groups[0] == "division officer":
                # application_detail = Applicationform.objects.filter(id=app_id)
                if application_detail[0].verify_range_officer==True:
                    application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
                    disapproved_by=request.user.id,disapproved_by_grp="By Division Officer",
                    application_status='R',division_officer = True,division_officer_date = date.today())
                else:
                    JsonResponse({'message':'Application cannot be disapproved as Forest Range Officer Action is Pending !'})
                # pass
            else:
                pass
            return JsonResponse({'message':'Application has been disapproved!'})
            # return render(request,"my_app/tigram/application_details.html",{'applicant':APPLICATION,'applications':application_detail,'message':'Application has been disapproved!'})

        vehicle_detail = Vehicle_detials.objects.filter(app_form_id=app_id)
        # transit_pass = TransitPass.object.filter(app_form_id=app_id)
        if application_detail :

            reason=request.data['reason']
            if groups[0] == "revenue officer":
                application_detail.update(
                reason_office = reason ,
                application_status = 'P',
                approved_by_revenue = request.user,
                verify_office = True,
                verify_office_date = date.today(),
                # transit_pass_id=transit_pass.id,
                # transit_pass_created_date = datetime.date.today(),
                )
            elif groups[0] == "deputy range officer":
                if application_detail[0].verify_office==True:

                    if application_detail[0].is_form_two ==False:
                        application_detail.update(
                        reason_depty_ranger_office = reason ,
                        application_status = 'P',
                        approved_by_deputy = request.user,
                        depty_range_officer = True,
                        deputy_officer_date = date.today(),
                        # transit_pass_id=transit_pass.id,
                        # transit_pass_created_date = datetime.date.today(),
                        )
                    else:
                        if application_detail[0].verify_deputy2 == True:
                        
                            application_detail.update(
                            reason_depty_ranger_office = reason ,
                            application_status = 'P',
                            approved_by_deputy = request.user,
                            depty_range_officer = True,
                            deputy_officer_date = date.today(),
                            # transit_pass_id=transit_pass.id,
                            # transit_pass_created_date = datetime.date.today(),
                            )
                        else:
                            application_detail.update(
                            reason_deputy2 = reason ,
                            application_status = 'P',
                            approved_by_deputy2 = request.user,
                            verify_deputy2 = True,
                            deputy2_date = date.today(),
                            # transit_pass_id=transit_pass.id,
                            # transit_pass_created_date = datetime.date.today(),
                            )

                else:
                    JsonResponse({'message':'Application cannot be approved as Revenue Officer Approval is Pending !'})
            # if vehicle_detail:
            elif groups[0] == "forest range officer":

                if application_detail[0].depty_range_officer==True:
                    if application_detail[0].other_state == False:
                        qr_code=get_qr_code(app_id)
                        print(qr_code,'-----QR')
                        qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
                        print(qr_img,'----qr_path')
                        is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
                        if is_timber:
                            for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
                                log_qr_code=get_log_qr_code(app_id,each_timber['id'])
                                print(log_qr_code,'-----LOG QR')

                                log_data='Log Details:\n'
                                log_data+='Application No. :-'+application_detail[0].application_no+'\n'
                                log_data+='Destination :-'+application_detail[0].destination_details+'\n'
                                log_data+='Species Name :-'+each_timber['species_of_tree']+'\n'
                                log_data+='Length :-'+str(each_timber['length'])+'\n'
                                log_data+='Girth :-'+str(each_timber['breadth'])+'\n'
                                log_data+='Volume :-'+str(each_timber['volume'])+'\n'
                                log_data+='Latitude :-'+str(each_timber['latitude'])+'\n'
                                log_data+='Longitude :-'+str(each_timber['longitude'])+'\n'
                                log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
                                print(log_qr_img,'----qr_path')
                                is_timber.filter(id=each_timber['id']).update(log_qr_code=log_qr_code,log_qr_code_img=log_qr_img)

                        if vehicle_detail:
                            # vehicle=vehicle_detail[0]
                            transit_pass=TransitPass.objects.create(
                                vehicle_reg_no=vehicle_detail[0].vehicle_reg_no,
                                driver_name = vehicle_detail[0].driver_name,
                                driver_phone = vehicle_detail[0].driver_phone,
                                mode_of_transport = vehicle_detail[0].mode_of_transport,
                                license_image = vehicle_detail[0].license_image,
                                photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        else:
                            transit_pass=TransitPass.objects.create(
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        application_detail.update(
                            reason_range_officer = reason ,
                            application_status = 'A',
                            approved_by = request.user,
                            verify_range_officer = True,
                            range_officer_date = date.today(),
                            transit_pass_id=transit_pass.id,
                            transit_pass_created_date = date.today(),
                            )
                    else:
                        application_detail.update(
                        reason_range_officer = reason ,
                        application_status = 'P',
                        approved_by = request.user,
                        verify_range_officer = True,
                        range_officer_date = date.today(),
                        )
					# JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
			# application_detail[0].save()
                else:
                    JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
            elif groups[0] == "division officer":
                if application_detail[0].verify_range_officer==True:
                    if application_detail[0].other_state == True:
                        qr_code=get_qr_code(app_id)
                        print(qr_code,'-----QR')
                        qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
                        print(qr_img,'----qr_path')
                        is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
                        if is_timber:
                            for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
                                log_qr_code=get_log_qr_code(app_id,each_timber['id'])
                                print(log_qr_code,'-----LOG QR')

                                log_data='Log Details:\n'
                                log_data+='Application No. :-'+application_detail[0].application_no+'\n'
                                log_data+='Destination :-'+application_detail[0].destination_details+'\n'
                                log_data+='Species Name :-'+each_timber['species_of_tree']+'\n'
                                log_data+='Length :-'+str(each_timber['length'])+'\n'
                                log_data+='Girth :-'+str(each_timber['breadth'])+'\n'
                                log_data+='Volume :-'+str(each_timber['volume'])+'\n'
                                log_data+='Latitude :-'+str(each_timber['latitude'])+'\n'
                                log_data+='Longitude :-'+str(each_timber['longitude'])+'\n'
                                log_qr_img=generate_log_qrcode_image(log_qr_code, settings.QRCODE_PATH, each_timber['id'],log_data)
                                print(log_qr_img,'----qr_path')
                                is_timber.filter(id=each_timber['id']).update(log_qr_code=log_qr_code,log_qr_code_img=log_qr_img)

                        if vehicle_detail:
                            # vehicle=vehicle_detail[0]
                            transit_pass=TransitPass.objects.create(
                                vehicle_reg_no=vehicle_detail[0].vehicle_reg_no,
                                driver_name = vehicle_detail[0].driver_name,
                                driver_phone = vehicle_detail[0].driver_phone,
                                mode_of_transport = vehicle_detail[0].mode_of_transport,
                                license_image = vehicle_detail[0].license_image,
                                photo_of_vehicle_with_number = vehicle_detail[0].photo_of_vehicle_with_number,
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        else:
                            transit_pass=TransitPass.objects.create(
                                state = application_detail[0].state,
                                district = application_detail[0].district,
                                taluka = application_detail[0].taluka,
                                block = application_detail[0].block,
                                village = application_detail[0].village,
                                qr_code = qr_code,
                                qr_code_img =qr_img, 
                                app_form_id = app_id
                            )
                        application_detail.update(
                            reason_division_officer = reason ,
                            application_status = 'A',
                            approved_by_division = request.user,
                            division_officer = True,
                            division_officer_date = date.today(),
                            transit_pass_id=transit_pass.id,
                            transit_pass_created_date = date.today(),
                            )
                    else:
                        JsonResponse({'message':'Application cannot be approved !'})
                        # JsonResponse({'message':'Application cannot be approved as Deputy Range Officer Approval is Pending !'})
                # application_detail[0].save()
                else:
                    JsonResponse({'message':'Application cannot be approved as Forest Range Officer Approval is Pending !'})
            else:
                pass
        return JsonResponse({'message':'Application has been approved!'})



class TreeSpeciesList(APIView):

    permission_classes = [permissions.AllowAny,]
 
    def get(self, request):

        application_detail = list(TreeSpecies.objects.all().values())
        # application_detail = list(Applicationform.objects.filter().values())

        validation_status = 'Success'
        validation_message = 'Data Feteched Successfully.'   
        return JsonResponse({'status': validation_status, 'message': validation_message,'data':application_detail} , safe=False)
      
