from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth  import login,authenticate,logout
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,HttpResponseNotFound
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import string
import random
import qrcode
# from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.template.loader import render_to_string
import tempfile
import pdfkit
from django.http import HttpResponse

import pdfkit
from django.contrib.auth.models import Group
from twilio.rest import Client
from twilio.rest import Client
from twilio import twiml
from django.contrib.auth.hashers import make_password

from django.db.models import Q
from django_pdfkit import PDFView
import datetime

from django.contrib.auth.backends import ModelBackend

from django.template.loader import get_template
from django.template import Context
import pdfkit
import os
from django.conf import settings
# from django.http import HttpResponse
# from pil import image
# from django.contrib.sessions.models import Sessions
# Create your views here.
# @login_required

IMAGE_TAG = {'AadharCard':settings.AADHAR_IMAGE_PATH,'Declaration':settings.DECLARATION_PATH,
			'License':settings.LICENSE_PATH,'LocationSketch':settings.LOCATION_SKETCH_PATH,
			'ProofOfOwnership':settings.PROOF_OF_OWNERSHIP_PATH,'RevenueApplication':settings.REVENUE_APPLICATION_PATH,
			'RevenueApproval':settings.REVENUE_APPROVAL_PATH,'TreeOwnership':settings.TREE_OWNERSHIP_PATH,
			'Signature':settings.SIGN_PATH,'QRCode' :settings.QRCODE_PATH,'Profile':settings.PROFILE_PATH,
			'PhotoProof':settings.PHOTO_PROOF_PATH

	}

from django.contrib.auth.decorators import user_passes_test

def upload_product_image_file(record_id, post_image, image_path, image_tag):
	image_name = ''
	image_path = settings.PROOF_OF_OWNERSHIP_PATH
	image_path = IMAGE_TAG[image_tag]
	if not os.path.exists(image_path):
		os.makedirs(image_path)
	image_name = None
	# j=random.randint(0,1000)
	# if post_image != '' and image_path != '' and image_tag != '' and record_id > 0:
	if post_image != '' and image_path != '' and image_tag != '' and record_id !='':
		try:
			filename = post_image.name
			filearr = filename.split('.')
			arr_len = len(filearr)

			if len(filearr) > 1 :
				file_name = filearr[0]
				file_ext = filearr[arr_len-1]
				#----------------------------------------#

				image_name =image_tag+"_"+str(record_id)+"_image."+str(file_ext)
				imagefile = str(image_path)+str(image_name)
				# from PIL import Image
				# import PIL

				# # creating a image object (main image)
				# im1 = Image.open(post_image)
				# print(im1)

				# # save a image using extension
				# im1 = im1.save(image_path+"geeks.jpg")
				#------- get content type ----#
				# if file_ext == 'jpg' or file_ext == 'jpeg':
				# 	content_type = 'image/jpeg'
				# if file_ext == 'png':
				# 	content_type = 'image/png'
				# if file_ext == 'gif':
				# 	content_type = 'image/gif'
				# if file_ext == 'svg':
				# 	content_type = 'image/svg+xml'

				#------------ STORE INVOICE --------------#
				with open(imagefile, 'wb+') as destination:
					print(post_image.chunks(),"---====--",destination)
					for chunk in post_image.chunks():
						print(destination,'----==')
						destination.write(chunk)
		except Exception as Error:
			print("----here",Error)
			pass

	return image_name

class MobilePhoneOrEmailModelBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        # the username could be either one of the two
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'mobile_phone': username}
        try:
            user = CustomUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return CustomUser.objects.get(pk=username)
        except CustomUser.DoesNotExist:
            return None

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='index')
    # return HttpResponseNotFound('<h1>Page Not Found! </h1>')

def group_permissions(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def has_permission(u):
        if u.is_authenticated:
            # if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
            # print(group_names,u.groups.values('id'))
            group_id = u.groups.values('id')
            # print(u.groups)
            if bool(RolePermission.objects.filter(method__method_name__in=group_names,group=group_id[0]['id'])) | u.is_superuser:
                return True
        return False

    return user_passes_test(has_permission, login_url='index')

# def load_tree_species(request):
# 	trees = TreeSpecies.objects.all().values_list(flat=True)
# 	return trees

def load_tree_species():
	trees = TreeSpecies.objects.all().values_list('name',flat=True)
	return trees

def is_user(user):
    return user.groups.filter(name='user').exists()

def is_staff_member(user):
    return user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer','division officer','field officer','state officer']).exists()

def is_admin(user):
    return user.groups.filter(name__in=['admin']).exists()

def user_login(request):
	context = {}
	if request.user.is_authenticated:
		# print(request.user)
		return HttpResponseRedirect(reverse('index'))
	if request.method == 'POST':
	# if 'name' not in request.session:
		username = request.POST.get('uname')
		password = request.POST.get('psw')
		if '@' in username:
			# username = username
			user = authenticate(request,email=username,password=password)
			if user:
				if is_user(user)!=True:
					context["message"] = "Provide valid credentials !"
					return render(request,'my_app/tigram/ulogin.html',context)
				login(request,user)
				user_details=CustomUser.objects.filter(id=request.user.id).values('name','user_id')
				request.session['username'] = user_details[0]['name']
				request.session['useremail'] = username
				request.session['userid'] =  user_details[0]['user_id']
				groups=request.user.groups.values_list('name',flat = True)
				print(groups,'---')
				if 'user' in groups:
					return HttpResponseRedirect(reverse('dashboard'))
				elif 'officer' in groups:
					# kwargs={'prod': prod})
					return HttpResponseRedirect(reverse('officer_dashboard'))
				else:
					return HttpResponseRedirect(reverse('officer_dashboard'))
			else:
				context["message"] = "Provide valid credentials !"
				return render(request,'my_app/tigram/ulogin.html',context)



		else:
			# username =
			print('mobile')
			eml=""
			em = CustomUser.objects.filter(phone=username).values('email')
			if em:

				print(em[0]["email"])
				eml= em[0]["email"]
			else:
				eml=""
			user = authenticate(email=eml,password=password)
			print(user)
			if user:
				if is_user(user)!=True:
					context["message"] = "Provide valid credentials !"
					return render(request,'my_app/tigram/ulogin.html',context)
				login(request,user)
				groups=request.user.groups.values_list('name',flat = True)
				print(groups,'---')
				if 'user' in groups:
					return HttpResponseRedirect(reverse('dashboard'))
				elif 'officer' in groups:
					# kwargs={'prod': prod})
					return HttpResponseRedirect(reverse('officer_dashboard'))
				else:
					return HttpResponseRedirect(reverse('officer_dashboard'))
			else:
				context["message"] = "Provide valid credentials !"
				return render(request,'my_app/tigram/ulogin.html',context)
	elif request.method == 'GET':
		login_type = request.GET.get('login_type')
		print(login_type,'--------')
		if login_type == 'officer':
			return render(request,'my_app/tigram/officerlogin.html',context)
		else:
			return render(request,'my_app/tigram/ulogin.html',context)
	else:

		pass
	return render(request,'my_app/tigram/ulogin.html',context)

def staff_login(request):
	context = {}
	if request.user.is_authenticated:
		# print(request.user)
		return HttpResponseRedirect(reverse('index'))
	if request.method == 'POST':
	# if 'name' not in request.session:
		username = request.POST.get('uname')
		password = request.POST.get('psw')
		if '@' in username:
			# username = username
			user = authenticate(request,email=username,password=password)
			if user:
				if is_staff_member(user)!=True:
					context["message"] = "Provide valid credentials !"
					return render(request,'my_app/tigram/officerlogin.html',context)
				login(request,user)
				groups=request.user.groups.values_list('name',flat = True)
				print(groups,'---')
				if 'user' in groups:
					return HttpResponseRedirect(reverse('dashboard'))
				elif 'officer' in groups:
					# kwargs={'prod': prod})
					return HttpResponseRedirect(reverse('officer_dashboard'))
				else:
					return HttpResponseRedirect(reverse('officer_dashboard'))
			else:
				context["message"] = "Provide valid credentials !"
				return render(request,'my_app/tigram/officerlogin.html',context)



		else:
			# username =
			print('mobile')
			eml=""
			em = CustomUser.objects.filter(phone=username).values('email')
			if em:

				print(em[0]["email"])
				eml= em[0]["email"]
			else:
				eml=""
			user = authenticate(email=eml,password=password)
			print(user)
			if user:
				if is_staff_member(user)!=True:
					context["message"] = "Provide valid credentials !"
					return render(request,'my_app/tigram/officerlogin.html',context)
				login(request,user)
				groups=request.user.groups.values_list('name',flat = True)
				print(groups,'---')
				if 'user' in groups:
					return HttpResponseRedirect(reverse('dashboard'))
				elif 'officer' in groups:
					# kwargs={'prod': prod})
					return HttpResponseRedirect(reverse('officer_dashboard'))
				else:
					return HttpResponseRedirect(reverse('officer_dashboard'))
			else:
				context["message"] = "Provide valid credentials !"
				return render(request,'my_app/tigram/officerlogin.html',context)

			# user = authenticate(request,phone=username,password=password)
		# uname=request.POST.get('uname')
		# print('Password:--',password)
		# user = authenticate(request,email=username,password=password)

	elif request.method == 'GET':
		#login_type = request.GET.get('login_type')
		#print(login_type,'--------')
		#if login_type == 'officer':
		#	return render(request,'my_app/tigram/officerlogin.html',context)
		#else:
			return render(request,'my_app/tigram/officerlogin.html',context)
	else:

		pass
	return render(request,'my_app/tigram/officerlogin.html',context)

@group_permissions('admin_login')
def super_login(request):
	print(request)
	login(request,user)
	groups=request.user.groups.values_list('name',flat = True)
	print(groups,'---')
	return HttpResponseRedirect(reverse('admin_dashboard'))

def admin_login(request):
	context = {}
	if request.user.is_authenticated:
		# print(request.user)
		return HttpResponseRedirect(reverse('index'))
	if request.method == 'POST':
	# if 'name' not in request.session:
		username = request.POST.get('uname')
		password = request.POST.get('psw')
		if '@' in username:
			# username = username
			user = authenticate(request,email=username,password=password)
			if user:
				# if is_admin(user)!=True:
				group_id = user.groups.values('id')
				print(group_id,'---grp')
				if not (user.is_superuser | RolePermission.objects.filter(method__method_name='admin_login',group=group_id[0]['id']).exists()) :
					context["message"] = "Provide valid credentials !"
					print(context)
					return render(request,'my_app/tigram/admin/login.html',context)
					# super_login(request,user)
				# return HttpResponseRedirect(reverse('super_login'))
				login(request,user)
				# groups=request.user.groups.values_list('name',flat = True)
				# print(groups,'---')
				return HttpResponseRedirect(reverse('admin_dashboard'))
			else:
				context["message"] = "Provide valid credentials !"
				print(context)
				return render(request,'my_app/tigram/admin/login.html',context)



		else:
			# username =
			print('mobile')
			eml=""
			em = CustomUser.objects.filter(phone=username).values('email')
			if em:

				print(em[0]["email"])
				eml= em[0]["email"]
			else:
				eml=""
			user = authenticate(email=eml,password=password)
			print(user)
			if user:
				if not (user.is_superuser | RolePermission.objects.filter(method__method_name='admin_login',group=group_id[0]['id']).exists()) :
					context["message"] = "Provide valid credentials !"
					print(context)
					return render(request,'my_app/tigram/admin/login.html',context)
				login(request,user)
				groups=request.user.groups.values_list('name',flat = True)
				print(groups,'---')

				return HttpResponseRedirect(reverse('admin_dashboard'))
			else:
				context["message"] = "Provide valid credentials !"
				print(context)
				return render(request,'my_app/tigram/admin/login.html',context)

			# user = authenticate(request,phone=username,password=password)
		# uname=request.POST.get('uname')
		# print('Password:--',password)
		# user = authenticate(request,email=username,password=password)

	elif request.method == 'GET':
		return render(request,'my_app/tigram/admin/login.html',context)

	return render(request,'my_app/tigram/admin/login.html',context)


@login_required(login_url='staff_login')
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('officer_dashboard')
def officer_dashboard(request):
	context = {}
	context['area_range_name']=''
	groups=request.user.groups.values_list('name',flat = True)
	application = Applicationform.objects.all()
	# pending_application_names = Applicationform.objects.exclude(application_status='A').values('name')
	# approved_application_names = Applicationform.objects.filter(application_status='A').values('name')
	# approved_application_dates = Applicationform.objects.filter(application_status='A').values('created_date').distinct()
	context['group'] = groups[0]
	context['current_page']='dashboard'
	if context['group'] == 'division officer':
		div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id).values_list('division_name',flat=True)
		context['area_range'] =Range.objects.filter(division_id=div_name[0]).values_list('name',flat=True)
	elif context['group'] == 'state officer':
		context['division_name'] = Division.objects.filter(is_delete=False).values_list('name',flat=True)
		context['area_range'] =Range.objects.filter(is_delete=False).values_list('name',flat=True)

		context['area_div_name']=request.GET.get('div_name',None)
		context['area_div_name']= "" if context['area_div_name'] == "" or context['area_div_name']==None else context['area_div_name']
		area_div_name = context['area_div_name']
		if area_div_name!=None:
			if area_div_name.isdigit():
				context['area_range'] = Range.objects.filter(division_id=area_div_name,is_delete=False).values_list('name',flat=True)
			else:
				context['area_range'] = Range.objects.filter(division__name__iexact=area_div_name,is_delete=False).values_list('name',flat=True)
				print(context['area_range'],'-----')	
		if len(context['area_range'])<1 and area_div_name=="" or area_div_name==None:
			context['area_range'] = Range.objects.filter(is_delete=False).values_list('name',flat=True)
	else:
		pass
	if groups[0] =='revenue officer':
		context['text_show'] = 'Revenue Officer'
		rev_range=RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		if not rev_range :
			return HttpResponseRedirect(reverse('index'))
		print(rev_range,'----')
		pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_office=False,area_range=rev_range[0].range_name.name,is_noc=False).order_by('-id')
		# approved_list = application.filter(verify_office=True,area_range=rev_range[0].range_name.name,deemed_approval=False).order_by('-id')
		approved_list = application.filter(area_range=rev_range[0].range_name.name,deemed_approval=False,is_noc=False,verify_office=True).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).order_by('-id')
		deemed_approved_list =application.filter(deemed_approval=True,area_range=rev_range[0].range_name.name).order_by('-id')
		noc_list =application.filter(is_noc=True,area_range=rev_range[0].range_name.name).order_by('-id')
	elif groups[0] =='deputy range officer':
		context['text_show'] = 'Deputy Range Officer'
		urange=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		if not urange :
			return HttpResponseRedirect(reverse('index'))
		pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(depty_range_officer=False,area_range=urange[0].range_name.name,is_noc=False).order_by('-id')
		#approved_list = application.filter(depty_range_officer=True,area_range=urange[0].range_name.name,deemed_approval=False).order_by('-id')
		approved_list = application.filter(depty_range_officer=True,area_range=urange[0].range_name.name,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).order_by('-id')
		deemed_approved_list =application.filter(deemed_approval=True,area_range=urange[0].range_name.name).order_by('-id')
		noc_list =application.filter(is_noc=True,area_range=urange[0].range_name.name).order_by('-id')
		# application = application.filter(verify_office=True)
	elif groups[0] =='forest range officer':
		context['text_show'] = 'Forest Range Officer'
		urange=ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		if not urange :
			return HttpResponseRedirect(reverse('index'))
		pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(verify_range_officer=False,area_range=urange[0].range_name.name,is_noc=False).order_by('-id')
		# approved_list = application.filter(application_status='A').filter(verify_range_officer=True,area_range=urange[0].range_name.name,deemed_approval=False).order_by('-id')
		approved_list = application.filter(verify_range_officer=True,area_range=urange[0].range_name.name,deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P')).order_by('-id')
		deemed_approved_list =application.filter(deemed_approval=True,area_range=urange[0].range_name.name).order_by('-id')
		noc_list =application.filter(is_noc=True,area_range=urange[0].range_name.name).order_by('-id')
		# application = application.filter(depty_range_officer=True)
	elif  groups[0] =='division officer':
		context['text_show'] = groups[0]
		area_range_name = request.GET.get('range_name')
		print(area_range_name,'----')
		if area_range_name=="" or area_range_name == None:
			pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).order_by('-id')
			approved_list = application.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P',other_state=False)).order_by('-id')
			deemed_approved_list =application.filter(deemed_approval=True).order_by('-id')
			noc_list =application.filter(is_noc=True).order_by('-id')
		else:
			context['area_range_name']=area_range_name
			pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(area_range__icontains=area_range_name).order_by('-id')
			approved_list = application.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P',other_state=False),area_range__icontains=area_range_name).order_by('-id')
			deemed_approved_list =application.filter(deemed_approval=True,area_range__icontains=area_range_name).order_by('-id')
			noc_list =application.filter(is_noc=True,area_range__icontains=area_range_name).order_by('-id')
	elif groups[0] =='admin' or groups[0] =='state officer':
		context['text_show'] = groups[0]
		area_range_name = request.GET.get('range_name')
		# context['area_div_name']=request.GET.get('div_name',None)
		# area_div_name = context['area_div_name']
		if area_div_name != None:
			if area_div_name.isdigit():
				context['area_range'] = Range.objects.filter(division_id=area_div_name,is_delete=False).values_list('name',flat=True)
			else:
				context['area_range'] = Range.objects.filter(division__name__iexact=area_div_name,is_delete=False).values_list('name',flat=True)
				print(context['area_range'],'-----')	
		if len(context['area_range'])<1 and area_div_name=="" or area_div_name==None:
				context['area_range'] = Range.objects.filter(is_delete=False).values_list('name',flat=True)

		# div_id=context['area_div_name']

		# print(area_range_name,'----')
		if area_div_name == "" or area_div_name == None:
			if area_range_name=="" or area_range_name == None:
				pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).order_by('-id')
				approved_list = application.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P',other_state=False)).order_by('-id')
				deemed_approved_list =application.filter(deemed_approval=True).order_by('-id')
				noc_list =application.filter(is_noc=True).order_by('-id')
			else:
				context['area_range_name']=area_range_name
				pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(area_range__icontains=area_range_name).order_by('-id')
				approved_list = application.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P',other_state=False),area_range__icontains=area_range_name).order_by('-id')
				deemed_approved_list =application.filter(deemed_approval=True,area_range__icontains=area_range_name).order_by('-id')
				noc_list =application.filter(is_noc=True,area_range__icontains=area_range_name).order_by('-id')
		else:
			if area_range_name=="" or area_range_name == None:
				pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(division__icontains=area_div_name).order_by('-id')
				approved_list = application.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P',other_state=False),division__icontains=area_div_name).order_by('-id')
				deemed_approved_list =application.filter(deemed_approval=True,division__icontains=area_div_name).order_by('-id')
				noc_list =application.filter(is_noc=True,division__icontains=area_div_name).order_by('-id')
			else:
				context['area_range_name']=area_range_name
				pending_list = application.exclude(Q(application_status='A')|Q(application_status='R')).filter(area_range__icontains=area_range_name,division__icontains=area_div_name).order_by('-id')
				approved_list = application.filter(deemed_approval=False,is_noc=False).filter(Q(application_status='A')|Q(application_status='R')|Q(application_status='P',other_state=False),area_range__icontains=area_range_name,division__icontains=area_div_name).order_by('-id')
				deemed_approved_list =application.filter(deemed_approval=True,area_range__icontains=area_range_name,division__icontains=area_div_name).order_by('-id')
				noc_list =application.filter(is_noc=True,area_range__icontains=area_range_name,division__icontains=area_div_name).order_by('-id')
	else:
		return HttpResponseRedirect(reverse('index'))
		context['text_show'] = 'Admin'
	# approved_list = application.filter(application_status='A').order_by('-id')
	context['user'] = request.user
	# context['application']
	# applicant = []
	# incr = 1
	# for each in application:
	# 	checkstatus = {}
	# 	checkstatus['sr'] =incr
	# 	checkstatus['applicant_no'] = each.id
	# 	checkstatus['application_no'] = each.application_no
	# 	checkstatus['applicant_name'] = each.name
	# 	checkstatus['created_date'] = each.created_date
	# 	checkstatus['application_status'] = each.get_application_status_display()
	# 	checkstatus['verification_status'] =each.application_status

	# 	# checkstatus['current_status'] =each.application_status

	# 	if each.reason_range_officer != '':
	# 		checkstatus['remark'] =  each.reason_range_officer
	# 		checkstatus['remark_date']= each.range_officer_date
	# 	elif each.reason_depty_ranger_office != '':
	# 		checkstatus['remark'] =  each.reason_depty_ranger_office
	# 		checkstatus['remark_date']= each.deputy_officer_date
	# 	elif each.reason_office != '':
	# 		checkstatus['remark'] =  each.reason_office
	# 		checkstatus['remark_date']= each.verify_office_date
	# 	else:
	# 		checkstatus['remark'] =  'N/A'
	# 		checkstatus['remark_date']= 'N/A'
	# 	if each.verify_range_officer == True:
	# 		checkstatus['current_status'] = 'Approved by Forest Range Officer' if each.application_status == 'A' else 'Rejected by Forest Range Officer'
	# 		checkstatus['current_status_by'] ='forest range officer'
	# 	elif each.depty_range_officer == True :
	# 		checkstatus['current_status'] =  'Approved by Deputy Range Officer and Forest Range Officer Approval Pending' if each.application_status == 'A' else 'Rejected by Deputy Range Officer'
	# 		checkstatus['current_status_by'] ='deputy range officer'
	# 	elif each.verify_office == True  :
	# 		checkstatus['current_status'] = 'Approved by Revenue Officer and Deputy Range Officer Approval Pending' if each.application_status == 'A' else 'Rejected by Revenue Officer'
	# 		checkstatus['current_status_by'] ='revenue officer'
	# 	else:
	# 		# checkstatus['current_status'] ='Revenue Officer Approval Pending'
	# 		checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
	# 	checkstatus['query'] = ''
	# 	checkstatus['tp_issue_date'] = each.transit_pass_created_date if each.application_status == 'A' else 'N/A'
	# 	checkstatus['tp_number'] = each.transit_pass_id
	# 	# if each.application_status != 'Approved':
	# 	# 	checkstatus['current_status'] ='Rejected'
	# 	# tp = TransitPass.objects.filter(app_form__by_user_id=each.id).order_by('-app_form_id')
	# 	applicant.append(checkstatus)
	# 	incr = incr+1
	# context['application'] = applicant
	pending_applicant = []
	incr1 = 1
	pending_application_names=[]
	pending_application_dates=[]
	pending_application_no=[]
	for each in pending_list:
		checkstatus = {}
		checkstatus['sr'] =incr1
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['applicant_name'] = each.name
		checkstatus['created_date'] = each.created_date
		checkstatus['application_status'] = each.get_application_status_display()
		checkstatus['verification_status'] =each.application_status
		pending_application_names.append(checkstatus['applicant_name'])
		pending_application_dates.append(checkstatus['created_date'])
		pending_application_no.append(checkstatus['application_no'])

		# checkstatus['current_status'] =each.application_status
		# checkstatus['days_left_for_approval'] = check
		if each.reason_division_officer != '':
			checkstatus['remark'] =  each.reason_division_officer
			checkstatus['remark_date']= each.division_officer_date
		elif each.reason_range_officer != '':
			checkstatus['remark'] =  each.reason_range_officer
			checkstatus['remark_date']= each.range_officer_date
		elif each.reason_depty_ranger_office != '':
			checkstatus['remark'] =  each.reason_depty_ranger_office
			checkstatus['remark_date']= each.deputy_officer_date
		elif each.reason_office != '':
			checkstatus['remark'] =  each.reason_office
			checkstatus['remark_date']= each.verify_office_date
		else:
			checkstatus['remark'] =  'N/A'
			checkstatus['remark_date']= 'N/A'
		if each.application_status == 'R' :
			checkstatus['remark'] = each.disapproved_reason

		if each.division_officer == True:
			checkstatus['current_status'] =  'Rejected by Division Officer' if each.application_status == 'R' else 'Approved by Division Officer'
			checkstatus['current_status_by'] ='division officer'
		elif each.verify_range_officer == True:
			if each.other_state==True:
				checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer and Division Officer Approval Pending'
				checkstatus['current_status_by'] ='forest range officer'
			else:
				checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer'
				checkstatus['current_status_by'] ='forest range officer'
		elif each.depty_range_officer == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer'  if each.application_status == 'R' else 'Approved by Deputy Range Officer and Forest Range Officer Approval Pending'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_deputy2 == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer at Stage 1'  if each.application_status == 'R' else 'Approved by Deputy Range Officer at Stage 1 and Deputy Range Officer Approval Pending at Stage 2'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_office == True  :
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Approved by Revenue Officer and Deputy Range Officer Approval Pending'
			checkstatus['current_status_by'] ='revenue officer'
		else:
			# checkstatus['current_status'] ='Revenue Officer Approval Pending'
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
		if each.verify_office != True  :
			checkstatus['days_left_for_approval'] = 'Not Generated'
			# checkstatus['verification_status'] =each.get_application_status_display()
		else:
			days_left=20-(date.today()-each.verify_office_date).days
			if days_left<1:
				checkstatus['days_left_for_approval'] = 0 #'TransitPass Expired'
				# checkstatus['verification_status'] ='TransitPass Expired'
			else:
				checkstatus['days_left_for_approval'] = 'Application Expired' if each.application_status == 'R' else days_left
				# checkstatus['verification_status'] =each.get_application_status_display()
		checkstatus['query'] = ''
		checkstatus['tp_issue_date'] = each.transit_pass_created_date if each.application_status == 'A' else 'N/A'
		checkstatus['tp_number'] = each.transit_pass_id
		checkstatus['is_form_two'] =each.is_form_two

		# if each.application_status != 'Approved':
		# 	checkstatus['current_status'] ='Rejected'
		# tp = TransitPass.objects.filter(app_form__by_user_id=each.id).order_by('-app_form_id')
		pending_applicant.append(checkstatus)
		incr1 = incr1+1
	context['pending_applicant'] = pending_applicant
	approved_applicant = []
	incr2 = 1
	approved_application_no=[]
	approved_application_names=[]
	approved_application_dates=[]
	for each in approved_list:
		checkstatus = {}
		checkstatus['sr'] =incr2
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['applicant_name'] = each.name
		checkstatus['created_date'] = each.created_date
		checkstatus['application_status'] = each.get_application_status_display()
		checkstatus['verification_status'] =each.application_status
		# pending_application_names.append(checkstatus['applicant_name'])
		approved_application_names.append(checkstatus['applicant_name'])
		approved_application_dates.append(checkstatus['created_date'])
		approved_application_no.append(checkstatus['application_no'])

		# checkstatus['current_status'] =each.application_status

		if each.reason_division_officer != '':
			checkstatus['remark'] =  each.reason_division_officer
			checkstatus['remark_date']= each.division_officer_date
		elif each.reason_range_officer != '':
			checkstatus['remark'] =  each.reason_range_officer
			checkstatus['remark_date']= each.range_officer_date
		elif each.reason_depty_ranger_office != '':
			checkstatus['remark'] =  each.reason_depty_ranger_office
			checkstatus['remark_date']= each.deputy_officer_date
		elif each.reason_office != '':
			checkstatus['remark'] =  each.reason_office
			checkstatus['remark_date']= each.verify_office_date
		else:
			checkstatus['remark'] =  'N/A'
			checkstatus['remark_date']= 'N/A'
		if each.application_status == 'R' :
			checkstatus['remark'] = each.disapproved_reason
		if each.division_officer == True:
			checkstatus['current_status'] =  'Rejected by Division Officer' if each.application_status == 'R' else 'Approved by Division Officer'
			checkstatus['current_status_by'] ='division officer'
		elif each.verify_range_officer == True:
			if each.other_state==True:
				checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer and Division Officer Approval Pending'
				checkstatus['current_status_by'] ='forest range officer'
			else:
				checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer'
				checkstatus['current_status_by'] ='forest range officer'
		elif each.depty_range_officer == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer'  if each.application_status == 'R' else 'Approved by Deputy Range Officer and Forest Range Officer Approval Pending'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_deputy2 == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer at Stage 1'  if each.application_status == 'R' else 'Approved by Deputy Range Officer at Stage 1 and Deputy Range Officer Approval Pending at Stage 2'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_office == True  :
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Approved by Revenue Officer and Deputy Range Officer Approval Pending'
			checkstatus['current_status_by'] ='revenue officer'
		else:
			# checkstatus['current_status'] ='Revenue Officer Approval Pending'
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
		checkstatus['query'] = ''
		checkstatus['tp_issue_date'] = each.transit_pass_created_date if each.application_status == 'A' else 'N/A'
		checkstatus['tp_number'] = each.transit_pass_id
		checkstatus['is_form_two'] =each.is_form_two
		# if each.application_status != 'Approved':
		# 	checkstatus['current_status'] ='Rejected'
		# tp = TransitPass.objects.filter(app_form__by_user_id=each.id).order_by('-app_form_id')
		approved_applicant.append(checkstatus)
		incr2 = incr2+1

	# deemed_approved_list
	deemed_approved_applicant = []
	incr3 = 1
	deemed_approved_application_no=[]
	deemed_approved_application_names=[]
	deemed_approved_application_dates=[]
	for each in deemed_approved_list:
		checkstatus = {}
		checkstatus['sr'] =incr3
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['applicant_name'] = each.name
		checkstatus['created_date'] = each.created_date
		checkstatus['application_status'] = each.get_application_status_display()
		checkstatus['verification_status'] =each.application_status
		# pending_application_names.append(checkstatus['applicant_name'])
		deemed_approved_application_names.append(checkstatus['applicant_name'])
		deemed_approved_application_dates.append(checkstatus['created_date'])
		deemed_approved_application_no.append(checkstatus['application_no'])

		# checkstatus['current_status'] =each.application_status

		if each.reason_range_officer != '':
			checkstatus['remark'] =  each.reason_range_officer
			checkstatus['remark_date']= each.range_officer_date
		elif each.reason_depty_ranger_office != '':
			checkstatus['remark'] =  each.reason_depty_ranger_office
			checkstatus['remark_date']= each.deputy_officer_date
		elif each.reason_office != '':
			checkstatus['remark'] =  each.reason_office
			checkstatus['remark_date']= each.verify_office_date
		else:
			checkstatus['remark'] =  'N/A'
			checkstatus['remark_date']= 'N/A'
		if each.application_status == 'R' :
			checkstatus['remark'] = each.disapproved_reason
		if each.verify_range_officer == True:
			checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer'
			checkstatus['current_status_by'] ='forest range officer'
		elif each.depty_range_officer == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer'  if each.application_status == 'R' else 'Approved by Deputy Range Officer and Forest Range Officer Approval Pending'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_office == True  :
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Approved by Revenue Officer and Deputy Range Officer Approval Pending'
			checkstatus['current_status_by'] ='revenue officer'
		else:
			# checkstatus['current_status'] ='Revenue Officer Approval Pending'
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
		checkstatus['query'] = ''
		checkstatus['tp_issue_date'] = each.transit_pass_created_date if each.application_status == 'A' else 'N/A'
		checkstatus['tp_number'] = each.transit_pass_id
		# if each.application_status != 'Approved':
		# 	checkstatus['current_status'] ='Rejected'
		# tp = TransitPass.objects.filter(app_form__by_user_id=each.id).order_by('-app_form_id')
		deemed_approved_applicant.append(checkstatus)
		incr3 = incr3+1

	noc_applicant = []
	incr4 = 1
	noc_application_no=[]
	noc_application_names=[]
	noc_application_dates=[]
	for each in noc_list:
		checkstatus = {}
		checkstatus['sr'] =incr3
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['applicant_name'] = each.name
		checkstatus['created_date'] = each.created_date
		# checkstatus['application_status'] = each.get_application_status_display()
		checkstatus['verification_status'] =each.application_status
		# pending_application_names.append(checkstatus['applicant_name'])
		noc_application_names.append(checkstatus['applicant_name'])
		noc_application_dates.append(checkstatus['created_date'])
		noc_application_no.append(checkstatus['application_no'])

		# checkstatus['current_status'] =each.application_status

		checkstatus['query'] = ''

		noc_applicant.append(checkstatus)
		incr4 = incr4+1
	# context['pending_applicant'] = pending_applicant
	context['approved_applicant'] = approved_applicant
	context['deemed_approved_applicant'] = deemed_approved_applicant
	context['noc_applicant'] = noc_applicant
	context['pending_application_no'] = set(pending_application_no)
	context['pending_application_names'] = set(pending_application_names)
	context['pending_application_date'] = set(pending_application_dates)
	context['approved_application_no'] = set(approved_application_no)
	context['approved_application_names'] = set(approved_application_names)
	context['approved_application_date'] = set(approved_application_dates)
	context['deemed_approved_application_no'] = set(deemed_approved_application_no)
	context['deemed_approved_application_names'] = set(deemed_approved_application_names)
	context['deemed_approved_application_date'] = set(deemed_approved_application_dates)
	context['noc_application_no'] = set(noc_application_no)
	context['noc_application_names'] = set(noc_application_names)
	context['noc_application_date'] = set(noc_application_dates)
	context['no_of_app']=Applicationform.objects.all().count()
	context['no_of_tp'] = TransitPass.objects.all().count()
	context['no_of_tp_pending'] = Applicationform.objects.filter(Q(application_status='S')|Q(application_status='P')).count()
	context['no_of_tp_rejected'] = Applicationform.objects.filter(application_status='R').count()
	# print(pending_applicant,'-========',approved_applicant)
	print('COntext:--',context)
	return render(request,"my_app/tigram/officerdash.html",context)


@login_required
@group_permissions('pending_applications')
def pending_applications(request):
	context = {}
	groups=request.user.groups.values_list('name',flat = True)

	application = Applicationform.objects.exclude(application_status='A').order_by('-id')
	if application:

		pending_applications = request.POST.get('sel_applicant01')
		filter_applicant = request.POST.get('filter_applicant')
		if pending_applications == 'application_no':
			application = application.filter(application_no__iexact=filter_applicant)
		elif pending_applications == 'application_name':
			application = application.filter(name__iexact=filter_applicant)
		elif pending_applications == 'application_date':
			application = application.filter(created_date=filter_applicant)
		else:
			pass
			# application = application.filter(name__iexact=filter_applicant)

		# application_no
	context['group'] = groups[0]
	if groups[0] =='revenue officer':
		context['text_show'] = 'Revenue Officer'
	elif groups[0] =='deputy range officer':
		context['text_show'] = 'Deputy Range Officer'
		# application = application.filter(verify_office=True)
	elif groups[0] =='forest range officer':
		context['text_show'] = 'Forest Range Officer'
		# application = application.filter(depty_range_officer=True)
	elif groups[0] =='admin':
		context['text_show'] = 'Admin'
	else:
		return HttpResponseRedirect(reverse('index'))
		context['text_show'] = 'Admin'
	context['user'] = request.user
	# context['application']
	applicant = []
	incr = 1
	for each in application:
		checkstatus = {}
		checkstatus['sr'] =incr
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['applicant_name'] = each.name
		checkstatus['created_date'] = each.created_date
		checkstatus['application_status'] = each.get_application_status_display()
		checkstatus['verification_status'] =each.application_status

		# checkstatus['current_status'] =each.application_status

		if each.reason_range_officer != '':
			checkstatus['remark'] =  each.reason_range_officer
			checkstatus['remark_date']= each.range_officer_date
		elif each.reason_depty_ranger_office != '':
			checkstatus['remark'] =  each.reason_depty_ranger_office
			checkstatus['remark_date']= each.deputy_officer_date
		elif each.reason_office != '':
			checkstatus['remark'] =  each.reason_office
			checkstatus['remark_date']= each.verify_office_date
		else:
			checkstatus['remark'] =  'N/A'
			checkstatus['remark_date']= 'N/A'
		if each.verify_range_officer == True:
			checkstatus['current_status'] = 'Approved by Forest Range Officer' if each.application_status == 'A' else 'Rejected by Forest Range Officer'
			checkstatus['current_status_by'] ='forest range officer'
		elif each.depty_range_officer == True :
			checkstatus['current_status'] =  'Approved by Deputy Range Officer and Forest Range Officer Approval Pending' if each.application_status == 'A' else 'Rejected by Deputy Range Officer'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_office == True  :
			checkstatus['current_status'] = 'Approved by Revenue Officer and Deputy Range Officer Approval Pending' if each.application_status == 'A' else 'Rejected by Revenue Officer'
			checkstatus['current_status_by'] ='revenue officer'
		else:
			# checkstatus['current_status'] ='Revenue Officer Approval Pending'
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
		checkstatus['query'] = ''
		checkstatus['tp_issue_date'] = each.transit_pass_created_date if each.application_status == 'A' else 'N/A'
		checkstatus['tp_number'] = each.transit_pass_id
		# if each.application_status != 'Approved':
		# 	checkstatus['current_status'] ='Rejected'
		# tp = TransitPass.objects.filter(app_form__by_user_id=each.id).order_by('-app_form_id')
		applicant.append(checkstatus)
		incr = incr+1
	context['application'] = applicant
		# application.save()
	return JsonResponse({'response_code':'success','application':context['application']})

@login_required
def approved_applications(request):
	context = {}
	groups=request.user.groups.values_list('name',flat = True)
	application = Applicationform.objects.filter(application_status='A').order_by('-id')
	if application:

		approved_applications = request.POST.get('sel_applicant01')
		filter_applicant = request.POST.get('filter_applicant')
		if approved_applications == 'application_no':
			application = application.filter(application_no__iexact=filter_applicant)
		elif approved_applications == 'application_name':
			application = application.filter(name__iexact=filter_applicant)
		elif approved_applications == 'application_date':
			application = application.filter(created_date=filter_applicant)
		else:
			pass
	context['group'] = groups[0]
	if groups[0] =='revenue officer':
		context['text_show'] = 'Revenue Officer'
	elif groups[0] =='deputy range officer':
		context['text_show'] = 'Deputy Range Officer'
		# application = application.filter(verify_office=True)
	elif groups[0] =='forest range officer':
		context['text_show'] = 'Forest Range Officer'
		# application = application.filter(depty_range_officer=True)
	elif groups[0] =='admin':
		context['text_show'] = 'Admin'
	else:
		return HttpResponseRedirect(reverse('index'))
		context['text_show'] = 'Admin'
	context['user'] = request.user
	# context['application']
	applicant = []
	incr = 1
	for each in application:
		checkstatus = {}
		checkstatus['sr'] =incr
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['applicant_name'] = each.name
		checkstatus['created_date'] = each.created_date
		checkstatus['application_status'] = each.get_application_status_display()
		checkstatus['verification_status'] =each.application_status

		# checkstatus['current_status'] =each.application_status

		if each.reason_range_officer != '':
			checkstatus['remark'] =  each.reason_range_officer
			checkstatus['remark_date']= each.range_officer_date
		elif each.reason_depty_ranger_office != '':
			checkstatus['remark'] =  each.reason_depty_ranger_office
			checkstatus['remark_date']= each.deputy_officer_date
		elif each.reason_office != '':
			checkstatus['remark'] =  each.reason_office
			checkstatus['remark_date']= each.verify_office_date
		else:
			checkstatus['remark'] =  'N/A'
			checkstatus['remark_date']= 'N/A'
		if each.verify_range_officer == True:
			checkstatus['current_status'] = 'Approved by Forest Range Officer' if each.application_status == 'A' else 'Rejected by Forest Range Officer'
			checkstatus['current_status_by'] ='forest range officer'
		elif each.depty_range_officer == True :
			checkstatus['current_status'] =  'Approved by Deputy Range Officer and Forest Range Officer Approval Pending' if each.application_status == 'A' else 'Rejected by Deputy Range Officer'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_office == True  :
			checkstatus['current_status'] = 'Approved by Revenue Officer and Deputy Range Officer Approval Pending' if each.application_status == 'A' else 'Rejected by Revenue Officer'
			checkstatus['current_status_by'] ='revenue officer'
		else:
			# checkstatus['current_status'] ='Revenue Officer Approval Pending'
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
		checkstatus['query'] = ''
		checkstatus['tp_issue_date'] = each.transit_pass_created_date if each.application_status == 'A' else 'N/A'
		checkstatus['tp_number'] = each.transit_pass_id
		# if each.application_status != 'Approved':
		# 	checkstatus['current_status'] ='Rejected'
		# tp = TransitPass.objects.filter(app_form__by_user_id=each.id).order_by('-app_form_id')
		applicant.append(checkstatus)
		incr = incr+1
	context['application'] = applicant
		# application.save()
	return JsonResponse({'response_code':'success','application':context['application']})
@login_required
# @group_required('user')
@group_permissions('user_dashboard')
def dashboard(request):
	context = {}
	groups=request.user.groups.values_list('name',flat = True)
	context['groups'] = groups
	context['user'] = request.user
	context['current_page']='dashboard'
	# print('COntext:--',context)
	return render(request,"my_app/tigram/dashboard.html",context)

# @login_required
# def admin_dashboard(request):
# 	context = {}
# 	groups=request.user.groups.values_list('name',flat = True)
# 	context['group'] = groups
# 	context['user'] = request.user
# 	# print('COntext:--',context)
# 	return render(request,"my_app/tigram/admin/dashboard.html",context)

@login_required
def user_logout(request):
	# print(request.user)
	if request.user!='':
		logout(request)
		return HttpResponseRedirect(reverse('index'))
	return redirect('index')

@login_required
def admin_logout(request):
	# print(request.user)
	if request.user!='':
		logout(request)
		return HttpResponseRedirect(reverse('admin_login'))
	return redirect('admin_login')

# group = Group.objects.get(name='groupname')
# user.groups.add(group)

#ApplicantFormat TG/Year/Mon/UserUniqueId/ApplicantNo

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


def signup(request):
	context = {}
	# if request.method =='GET':
	if not request.is_ajax():
		context['proof_list'] = PhotoProof.objects.all().values()
	context['response_code']=''
	if request.method =='POST':
		username = request.POST.get('uname')
		email = request.POST.get('email')
		phone = request.POST.get('number')
		passwd = request.POST.get('psw')
		passwd2 = request.POST.get('psw2')
		address = request.POST.get('address')
		photo_proof_no = request.POST.get('photo_proof_no')
		photo_proof_name = request.POST.get('photo_proof_select')
		photo_proof_doc = request.FILES.get('photo_proof')
		# print('Request',request.POST)
		if '@' not in email or '.' not in email :
			context['response_code'] = 'error'
			context['message'] = 'Invalid Email Id'
		if passwd2!=passwd :
			context['response_code'] = 'error'
			context['message'] = 'Password and Confirm Password Must Match!'
		if context['response_code'] != '':
			if request.is_ajax():
					return False,context
			return render(request,"my_app/tigram/registration.html",context)
		try :
			email=email.lower().strip()
			phone=phone.strip()
			username=username.strip()
			address = address.strip()
			passwd = passwd.strip()
			if CustomUser.objects.filter(Q(email=email)|Q(phone=phone)).exists():
				context['response_code'] = 'error'
				context['message'] = 'User already exists!'
				if request.is_ajax():
					return False,context
				return render(request,"my_app/tigram/registration.html",context)
			# print('----here001----')
			proof_type = PhotoProof.objects.filter(name__iexact=photo_proof_name)
			# print(proof_type,'----qs',photo_proof_name)
			user_create = CustomUser.objects.create_user(email,passwd,
				name=username,phone=phone,address=address,
				photo_proof_no=photo_proof_no,photo_proof_name=photo_proof_name,
				photo_proof_type_id=proof_type[0].id
				)
			# print('----here1----')
			generated_id = generate_user_id(user_create.id)
			user_create.user_id = generated_id
			make_id = str(user_create.id)+'r'
			url = '/static/media/upload/'
			# print('----here2----')
			saved_photo=upload_product_image_file(make_id,photo_proof_doc,url,'PhotoProof')
			user_create.photo_proof_img = saved_photo
			# UserId:Date01
			# user_create.user_id=
			user_create.save()
			# print('----here3----')
			group = Group.objects.get(name='user')
			user_create.groups.add(group)
			# print('----here4----')
			context['message']= 'User created successfully! '
			context['response_code'] ='success'
			if request.is_ajax():
				# context['proof_list']=list(context['proof_list'])
				return JsonResponse(context)
			# login(request,user_create)
			return render(request,'my_app/tigram/ulogin.html',context)
			# return HttpResponseRedirect(reverse('user_login'))
		except Exception as Error:
			print(Error)
			context['message']= 'User has not been created! '
			context['response_code'] ='error'
			if request.is_ajax():
				# context['proof_list']=list(context['proof_list'])
				return JsonResponse(context)
			return render(request,"my_app/tigram/registration.html",context)
	# print(user_create,'---Created')
	return render(request,"my_app/tigram/registration.html",context)



def create_new_user(request,group_name):
	context={}
	if request.method =='POST':
		username = request.POST.get('uname')
		email = request.POST.get('email')
		phone = request.POST.get('number')
		passwd = request.POST.get('psw')
		passwd2 = request.POST.get('psw2')
		address = request.POST.get('address')
		photo_proof_no = request.POST.get('photo_proof_no')
		photo_proof_name = request.POST.get('photo_proof_select')
		photo_proof_doc = request.FILES.get('photo_proof')
		# print('Request',request.POST)
		if '@' not in email or '.' not in email :
			context['response_code'] = 'error'
			context['message'] = 'Invalid Email Id'
		if passwd2!=passwd :
			context['response_code'] = 'error'
			context['message'] = 'Password and Confirm Password Must Match!'

		if 'response_code' in context:
			return False,context
			# return JsonResponse(context)
			# return render(request,"my_app/tigram/registration.html",context)
		try :
			email=email.lower().strip()
			phone=phone.strip()
			username=username.strip()
			address = address.strip()
			passwd = passwd.strip()
			# print('----here001----')
			if CustomUser.objects.filter(Q(email=email)|Q(phone=phone)).exists():
				context['response_code'] = 'error'
				context['message'] = 'User already exists!'
				return False,context
				# return JsonResponse(context)
				# return render(request,"my_app/tigram/registration.html",context)
			proof_type = PhotoProof.objects.filter(name__iexact=photo_proof_name)
			# print(proof_type,'----qs',photo_proof_name)
			user_create = CustomUser.objects.create_user(email,passwd,
				name=username,phone=phone,address=address,
				photo_proof_no=photo_proof_no,photo_proof_name=photo_proof_name,
				photo_proof_type_id=proof_type[0].id
				)
			# print('----here1----')
			generated_id = generate_user_id(user_create.id)
			user_create.user_id = generated_id
			make_id = str(user_create.id)+'r'
			url = '/static/media/upload/'
			# print('----here2----')
			saved_photo=upload_product_image_file(make_id,photo_proof_doc,url,'PhotoProof')
			user_create.photo_proof_img = saved_photo
			# UserId:Date01
			# user_create.user_id=
			user_create.save()
			# print('----here3----')
			group = Group.objects.get(name=group_name)
			user_create.groups.add(group)
			# print('----here4----')
			context['message']= 'User created successfully! '
			context['response_code'] ='success'
			return user_create,context
		except Exception as error:
			print(error)
			context['message']= 'User not created.Please check data entered!'
			context['response_code'] ='error'
			return True,context

	else:
		return True,context
	return True,context

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer','user')
@group_permissions('application_form')
def application_form(request):
	context={}
	context['proof_list'] = PhotoProof.objects.all().values()
	context['trees_species'] = TreeSpecies.objects.filter(is_noc=False,is_delete=False).values('name')
	context['range_areas'] = Range.objects.filter(is_delete=False).values('name')
	context['division_areas'] = Division.objects.filter(is_delete=False).values('name')
	context['district_name'] = District.objects.all().values('district_name')
	context['taluka_name'] = Taluka.objects.all().values('taluka_name')
	context['Village'] = Village.objects.all().values('village_name')


	groups=request.user.groups.values_list('name',flat = True)
	context['groups'] = groups
	print(request.user)
	if request.method == "POST":
		name=request.POST.get('uname')
		address=request.POST.get('add')
		survey_no=request.POST.get('sno')
		tree_proposed=request.POST.get('treep')
		village=request.POST.get('village')
		district=request.POST.get('dist')
		block=request.POST.get('block')
		taluka=request.POST.get('taluka')
		division=request.POST.get('division')
		area_range=request.POST.get('area_range')
		pincode=request.POST.get('pincode')
		# print(request.FILES)
		ownership_proof_img=request.FILES.get('ownership_proof_img')
		revenue_application_img=request.FILES.get('revenue_application_img')
		revenue_approval_img=request.FILES.get('revenue_approval_img')
		declaration_img=request.FILES.get('declaration_img')
		location_sketch_img=request.FILES.get('location_sketch_img')
		tree_ownership_img=request.FILES.get('tree_ownership_img')
		aadhar_card_img=request.FILES.get('aadhar_card_img')
		signature_img = request.FILES.get('signature_img')
		lic_img=request.FILES.get('lic_img')
		tree_species=request.POST.get('tree_species')
		purpose = request.POST.get('purpose_cut')
		veh_reg=request.POST.get('veh_reg')
		driver_name= request.POST.get('driver_name')
		phone = request.POST.get('phn')
		mode = request.POST.get('mode')
		species = request.POST.getlist('species[]')
		length = request.POST.getlist('length[]')
		breadth = request.POST.getlist('breadth[]')
		volume = request.POST.getlist('volume[]')
		latitude = request.POST.getlist('latitude[]')
		longitude = request.POST.getlist('longitude[]')
		is_vehicle = request.POST.get('option')
		is_log = request.POST.get('log_option')
		is_cut = request.POST.get('trees_cut')
		destination_state = request.POST.get('dest_state')
		# treep = request.POST.get('treep')
		destination_address = request.POST.get('destination_details')
		print(species,'\nlength',length,'\nbreadth',breadth)
		# Timberlogdetails.objects.create()
		tlog=[]

		#ggg
		# print("-------img-----",img)
		# url = settings.MEDIA_URL+'upload/aadhar_card/'

		url='static/media/'
		try:
			application = Applicationform.objects.create(
				name=name,address=address,destination_details=destination_address,
				survey_no=survey_no,village=village,total_trees=tree_proposed,
				district=district,species_of_trees=tree_species,pincode=pincode,
				purpose=purpose,block=block,taluka=taluka,division=division,destination_state=destination_state,
				area_range=area_range,by_user=request.user
				)
			saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
			saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
			saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
			saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
			saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
			saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
			saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
			saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
			application.proof_of_ownership_of_tree=saved_image_6


			image_doc=image_documents.objects.create(app_form=application,
					revenue_approval=saved_image_2,declaration=saved_image_1,
					revenue_application=saved_image_3,location_sktech=saved_image_4,
					tree_ownership_detail=saved_image_5,aadhar_detail=saved_image,
					signature_img=saved_image_8
				)
			# application.revenue_approval = True
			# application.declaration = True
			uid=request.user.id
			application.application_no=generate_app_id(uid,application.id)
			application.signature_img = True
			application.revenue_application = True
			application.location_sktech = True
			application.tree_ownership_detail = True
			application.aadhar_detail = True
			if destination_state != 'Kerala':
				application.other_state = True
			if is_cut =='yes' :
				application.trees_cutted= True
			else:
				application.trees_cutted= False
			if is_log == 'yes':
				if len(species) >0 :
					for i in range(len(species)):
						timber = Timberlogdetails(appform=application,species_of_tree=species[i],
						length=length[i],volume=volume[i],breadth=breadth[i],latitude=latitude[i],longitude=longitude[i])
						tlog.append(timber)
					Timberlogdetails.objects.bulk_create(tlog)
			application.save()
			if is_vehicle == 'yes':
				saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
				vehicle = Vehicle_detials.objects.create(app_form=application,
					license_image=saved_image_7,vehicle_reg_no=veh_reg,
					driver_name=driver_name,driver_phone=phone,
					mode_of_transport=mode
					)
			# print("created")
			messages.add_message(request, messages.SUCCESS, 'Application Submitted Successfully!')
			return render(request,"my_app/tigram/form3.html",context)
		except Exception as err:
			print(err)
			messages.add_message(request, messages.ERROR, 'Application has not submitted!')
			return render(request,"my_app/tigram/form3.html",context)


		# return HttpResponseRedirect(reverse('dashboard'))
	# return render(request,"my_app/tigram/form2.html",context)
	return render(request,"my_app/tigram/form3.html",context)

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer','user')
# @group_permissions('notified_application_form')
def notified_application_form(request):
	context={}
	context['proof_list'] = PhotoProof.objects.all().values()
	context['trees_species'] = TreeSpecies.objects.filter(is_noc=False,is_delete=False).values('name','id')
	context['range_areas'] = Range.objects.filter(is_delete=False).values('name')
	context['division_areas'] = Division.objects.filter(is_delete=False).values('name')
	context['district_name'] = District.objects.all().values('district_name')
	context['taluka_name'] = Taluka.objects.all().values('taluka_name')
	context['Village'] = Village.objects.all().values('village_name')


	groups=request.user.groups.values_list('name',flat = True)
	context['groups'] = groups
	print(request.user)
	if request.method == "POST":
		name=request.POST.get('uname')
		address=request.POST.get('add')
		survey_no=request.POST.get('sno')
		tree_proposed=request.POST.get('treep')
		village=request.POST.get('village')
		district=request.POST.get('dist')
		block=request.POST.get('block')
		taluka=request.POST.get('taluka')
		division=request.POST.get('division')
		area_range=request.POST.get('area_range')
		pincode=request.POST.get('pincode')
		# print(request.FILES)
		ownership_proof_img=request.FILES.get('ownership_proof_img')
		revenue_application_img=request.FILES.get('revenue_application_img')
		revenue_approval_img=request.FILES.get('revenue_approval_img')
		declaration_img=request.FILES.get('declaration_img')
		location_sketch_img=request.FILES.get('location_sketch_img')
		tree_ownership_img=request.FILES.get('tree_ownership_img')
		aadhar_card_img=request.FILES.get('aadhar_card_img')
		signature_img = request.FILES.get('signature_img')
		lic_img=request.FILES.get('lic_img')
		tree_species=request.POST.get('tree_species')
		purpose = request.POST.get('purpose_cut')
		veh_reg=request.POST.get('veh_reg')
		driver_name= request.POST.get('driver_name')
		phone = request.POST.get('phn')
		mode = request.POST.get('mode')
		is_cut = request.POST.get('trees_cut')

		# if is_cut == 'yes':
		# 	species = request.POST.getlist('species[]')
		# 	length = request.POST.getlist('length[]')
		# 	breadth = request.POST.getlist('breadth[]')
		# 	volume = request.POST.getlist('volume[]')
		# 	latitude = request.POST.getlist('latitude[]')
		# 	longitude = request.POST.getlist('longitude[]')
		# else:
			# species = request.POST.getlist('species02[]')
			# latitude = request.POST.getlist('latitude02[]')
			# longitude = request.POST.getlist('longitude02[]')
		species = request.POST.getlist('species02[]')
		latitude = request.POST.getlist('latitude02[]')
		longitude = request.POST.getlist('longitude02[]')

		is_vehicle = request.POST.get('option')
		is_log = request.POST.get('log_option')
		destination_state = request.POST.get('dest_state')
		# treep = request.POST.get('treep')
		destination_address = request.POST.get('destination_details')
		# print(species,'\nlength',length,'\nbreadth',breadth)
		# Timberlogdetails.objects.create()
		tlog=[]

		#ggg
		# print("-------img-----",img)
		# url = settings.MEDIA_URL+'upload/aadhar_card/'

		url='static/media/'
		try:
			tree_proposed=len(species)
			application = Applicationform.objects.create(
				name=name,address=address,destination_details=destination_address,
				survey_no=survey_no,village=village,total_trees=tree_proposed,
				district=district,species_of_trees=tree_species,pincode=pincode,
				purpose=purpose,block=block,taluka=taluka,division=division,
				area_range=area_range,by_user=request.user
				)
			saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
			saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
			saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
			saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
			saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
			saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
			saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
			saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
			application.proof_of_ownership_of_tree=saved_image_6


			image_doc=image_documents.objects.create(app_form=application,
					revenue_approval=saved_image_2,declaration=saved_image_1,
					revenue_application=saved_image_3,location_sktech=saved_image_4,
					tree_ownership_detail=saved_image_5,aadhar_detail=saved_image,
					signature_img=saved_image_8
				)
			# application.revenue_approval = True
			# application.declaration = True
			uid=request.user.id
			application.application_no=generate_app_id(uid,application.id)
			application.signature_img = True
			application.revenue_application = True
			application.location_sktech = True
			application.tree_ownership_detail = True
			application.aadhar_detail = True
			application.is_form_two =True
			if destination_state != 'Kerala':
				application.other_state = True
			if is_cut =='yes' :
				application.trees_cutted= True
			else:
				application.trees_cutted= False
			# if is_log == 'yes':
			# 	if len(species) >0 :
			# 		for i in range(len(species)):
			# 			timber = Timberlogdetails(appform=application,species_of_tree=species[i],
			# 			length=length[i],volume=volume[i],breadth=breadth[i],latitude=latitude[i],longitude=longitude[i])
			# 			tlog.append(timber)
			# 		Timberlogdetails.objects.bulk_create(tlog)
			if len(species) >0 :
				for i in range(len(species)):
					timber = Species_geodetails(appform=application,species_tree_id=species[i],
								latitude=latitude[i],longitude=longitude[i])
					tlog.append(timber)
				Species_geodetails.objects.bulk_create(tlog)
			application.save()
			if is_vehicle == 'yes':
				saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
				vehicle = Vehicle_detials.objects.create(app_form=application,
					license_image=saved_image_7,vehicle_reg_no=veh_reg,
					driver_name=driver_name,driver_phone=phone,
					mode_of_transport=mode
					)
			# print("created")
			messages.add_message(request, messages.SUCCESS, 'Application Submitted Successfully!')
			return render(request,"my_app/tigram/notified_form.html",context)
		except Exception as err:
			print(err)
			messages.add_message(request, messages.ERROR, 'Application has not submitted!')
			return render(request,"my_app/tigram/notified_form.html",context)


		# return HttpResponseRedirect(reverse('dashboard'))
	# return render(request,"my_app/tigram/form2.html",context)
	return render(request,"my_app/tigram/notified_form.html",context)

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer','user')
# @group_permissions('noc_application_form')
def noc_application_form(request):
	context={}
	context['proof_list'] = PhotoProof.objects.all().values()
	context['trees_species'] = TreeSpecies.objects.filter(is_noc=True,is_delete=False).values('name')
	context['range_areas'] = Range.objects.filter(is_delete=False).values('name')
	context['district_name'] = District.objects.all().values('district_name')

	context['division_areas'] = Division.objects.filter(is_delete=False).values('name')
	groups=request.user.groups.values_list('name',flat = True)
	context['groups'] = groups
	print(request.user)
	if request.method == "POST":
		name=request.POST.get('uname')
		address=request.POST.get('add')
		survey_no=request.POST.get('sno')
		tree_proposed=request.POST.get('treep')
		village=request.POST.get('village')
		district=request.POST.get('dist')
		block=request.POST.get('block')
		taluka=request.POST.get('taluka')
		division=request.POST.get('division')
		area_range=request.POST.get('area_range')
		pincode=request.POST.get('pincode')
		# print(request.FILES)
		# ownership_proof_img=request.FILES.get('ownership_proof_img')
		# revenue_application_img=request.FILES.get('revenue_application_img')
		# revenue_approval_img=request.FILES.get('revenue_approval_img')
		# declaration_img=request.FILES.get('declaration_img')
		# location_sketch_img=request.FILES.get('location_sketch_img')
		# tree_ownership_img=request.FILES.get('tree_ownership_img')
		aadhar_card_img=request.FILES.get('aadhar_card_img')
		signature_img = request.FILES.get('signature_img')
		# lic_img=request.FILES.get('lic_img')
		tree_species=request.POST.get('tree_species')
		purpose = request.POST.get('purpose_cut')
		veh_reg=request.POST.get('veh_reg')
		driver_name= request.POST.get('driver_name')
		phone = request.POST.get('phn')
		mode = request.POST.get('mode')
		species = request.POST.getlist('species[]')
		length = request.POST.getlist('length[]')
		breadth = request.POST.getlist('breadth[]')
		volume = request.POST.getlist('volume[]')
		latitude = request.POST.getlist('latitude[]')
		longitude = request.POST.getlist('longitude[]')
		is_vehicle = request.POST.get('option')
		is_log = request.POST.get('log_option')
		is_cut = request.POST.get('trees_cut')
		# treep = request.POST.get('treep')
		destination_address = request.POST.get('destination_details')
		print(species,'\nlength',length,'\nbreadth',breadth)
		# Timberlogdetails.objects.create()
		tlog=[]

		#ggg
		# print("-------img-----",img)
		# url = settings.MEDIA_URL+'upload/aadhar_card/'

		url='static/media/'
		try:
			application = Applicationform.objects.create(
				name=name,address=address,destination_details=destination_address,
				survey_no=survey_no,village=village,total_trees=tree_proposed,
				district=district,species_of_trees=tree_species,pincode=pincode,
				purpose=purpose,block=block,taluka=taluka,division=division,destination_state=destination_state,
				area_range=area_range,by_user=request.user,is_noc=True
				)
			saved_image=upload_product_image_file(application.id,aadhar_card_img,url,'AadharCard')
			# saved_image_2=upload_product_image_file(application.id,revenue_approval_img,url,'RevenueApproval')
			# saved_image_1=upload_product_image_file(application.id,declaration_img,url,'Declaration')
			# saved_image_3=upload_product_image_file(application.id,revenue_application_img,url,'RevenueApplication')
			# saved_image_4=upload_product_image_file(application.id,location_sketch_img,url,'LocationSketch')
			# saved_image_5=upload_product_image_file(application.id,tree_ownership_img,url,'TreeOwnership')
			# saved_image_6=upload_product_image_file(application.id,ownership_proof_img,url,'ProofOfOwnership')
			saved_image_8=upload_product_image_file(application.id,signature_img,url,'Signature')
			# application.proof_of_ownership_of_tree=saved_image_6


			image_doc=image_documents.objects.create(app_form=application,
					# revenue_approval=saved_image_2,declaration=saved_image_1,
					# revenue_approval='no_image',
					# revenue_application=saved_image_3,location_sktech=saved_image_4,
					# tree_ownership_detail=saved_image_5,
					aadhar_detail=saved_image,
					signature_img=saved_image_8
				)
			# application.revenue_approval = True
			# application.declaration = True
			uid=request.user.id
			application.application_no=generate_noc_app_id(uid,application.id)
			application.signature_img = True
			# application.revenue_application = True
			# application.location_sktech = True
			# application.tree_ownership_detail = True
			application.aadhar_detail = True
			if is_cut =='yes' :
				application.trees_cutted= True
			else:
				application.trees_cutted= False
			if is_log == 'yes':
				if len(species) >0 :
					for i in range(len(species)):
						timber = Timberlogdetails(appform=application,species_of_tree=species[i],
						length=length[i],volume=volume[i],breadth=breadth[i],latitude=latitude[i],longitude=longitude[i])
						tlog.append(timber)
					Timberlogdetails.objects.bulk_create(tlog)
			application.save()
			qr_code=get_qr_code(application.id)
			print(qr_code,'-----QR')
			qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, application.id)
			print(qr_img,'----qr_path')
			application_detail = Applicationform.objects.filter(id=application.id)
			if is_vehicle == 'yes':
				# saved_image_7=upload_product_image_file(application.id,lic_img,url,'License')
				vehicle = Vehicle_detials.objects.create(app_form=application,
					# license_image=saved_image_7,
					vehicle_reg_no=veh_reg,
					driver_name=driver_name,driver_phone=phone,
					mode_of_transport=mode
					)

				transit_pass=TransitPass.objects.create(
						vehicle_reg_no=veh_reg,
						driver_name =driver_name,
						driver_phone = phone,
						mode_of_transport = mode,
						state = application_detail[0].state,
						district = application_detail[0].district,
						taluka = application_detail[0].taluka,
						block = application_detail[0].block,
						village = application_detail[0].village,
						qr_code = qr_code,
						qr_code_img =qr_img,
						app_form_id = application.id
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
						app_form_id = application.id
					)
			application_detail.update(
					# reason_range_officer = reason ,
					application_status = 'A',
					# approved_by = request.user,
					# verify_range_officer = True,
					# range_officer_date = date.today(),
					transit_pass_id=transit_pass.id,
					transit_pass_created_date = date.today(),
					)
			# print("created")
			messages.add_message(request, messages.SUCCESS, 'Application Submitted Successfully!')
			return render(request,"my_app/tigram/noc_form.html",context)
		except Exception as err:
			print(err)
			messages.add_message(request, messages.ERROR, 'Application has not submitted!')
			return render(request,"my_app/tigram/noc_form.html",context)


		# return HttpResponseRedirect(reverse('dashboard'))
	# return render(request,"my_app/tigram/form2.html",context)
	return render(request,"my_app/tigram/noc_form.html",context)

@login_required
@group_required('revenue officer','deputy range officer','forest range officer')
# @group_permissions('application_form')
def application_list(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	context['group'] = groups
	applications = Applicationform.objects.all()
	paginator = Paginator(applications, 3)
	# paginator = Paginator(applications, 3)
	page = 3
	try:
		applications_list = paginator.page(page)
	except PageNotAnInteger:
		applications_list = paginator.page(1)
	except EmptyPage:
		applications_list = paginator.page(paginator.num_pages)

	return render(request,"my_app/tigram/application_list.html",{'applications':applications_list})

APPLICATION={
	'name': 'NAME',
	'address' : 'ADDRESS'
}

@login_required
# @group_required('user')
@group_permissions('update_vehicle')
def update_vehicle(request,app_id):
	groups=request.user.groups.values_list('name',flat = True)
	application_detail = Applicationform.objects.filter(id=app_id)
	if not application_detail:
		message = "Not Updated!"
		return JsonResponse(
		{'message':message,'status':'200'})
	# license_image=
	veh_reg=request.POST.get('veh_reg')
	driver_name= request.POST.get('driver_name')
	phone = request.POST.get('phn')
	mode = request.POST.get('mode')
	lic_img=request.FILES.get('lic_img',None)
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
					vehicle_reg_no=veh_reg,	license_image=license_image,
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
	# transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
	return JsonResponse(
		{'vehicle':vehicle,'message':message,'pic_url':license_image,'status':'200'})
	# return render(request,"my_app/tigram/userviewapplication.html",
	# 	{'vehicle':vehicle,'trees_species_list':trees_species_list})

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('application_view')
def application_view(request,app_id):
	groups=request.user.groups.values_list('name',flat = True)
	application_detail = Applicationform.objects.filter(id=app_id)
	trees_species_list = TreeSpecies.objects.all().values('name')
	image_document=[]
	if image_documents.objects.filter(app_form_id=app_id).exists():
		image_document = image_documents.objects.filter(app_form_id=app_id)[0]
	# if application_detail:
	vehicle = Vehicle_detials.objects.filter(app_form_id=app_id)
	isvehicle=''
	if vehicle:
		vehicle=vehicle[0]
	else:
		isvehicle = 'Not Applicable'
	is_timberlog=''
	timber_log = Timberlogdetails.objects.filter(appform_id=app_id)
	if timber_log:
		timber_log=timber_log.values()
	else:
		is_timberlog='N/A'
	# transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
	app_status =False
	if application_detail[0].application_status=='A' or application_detail[0].application_status =='R':
		app_status=True
	transit_pass_exist = False
	if groups[0] == "revenue officer" and application_detail[0].verify_office == True:
		transit_pass_exist = True
	elif groups[0] == "deputy range officer" and application_detail[0].depty_range_officer == True:
		transit_pass_exist = True
	elif groups[0] == "forest range officer" and application_detail[0].verify_range_officer == True:
		transit_pass_exist = True
	else:
		pass
	print(transit_pass_exist,'----TP')
	return render(request,"my_app/tigram/viewapplication.html",{'formtype':'view','applicant':APPLICATION,
		'applications':application_detail,'image_documents':image_document,'groups':groups,'app_status':app_status,
		'transit_pass_exist':transit_pass_exist,'vehicle':vehicle,'timber_log':timber_log,
		'trees_species_list':trees_species_list,'isvehicle':isvehicle,'is_timberlog':is_timberlog})

@login_required
# @group_required('user')
@group_permissions('application_userview')
def application_userview(request,app_id):
	groups=request.user.groups.values_list('name',flat = True)
	application_detail = Applicationform.objects.filter(id=app_id)
	trees_species_list = TreeSpecies.objects.all().values('name')
	image_document=[]
	if image_documents.objects.filter(app_form_id=app_id).exists():
		image_document = image_documents.objects.filter(app_form_id=app_id)[0]
	# if application_detail:
	vehicle = Vehicle_detials.objects.filter(app_form_id=app_id)
	isvehicle=''
	if vehicle:
		vehicle=vehicle[0]
	else:
		isvehicle = 'Not Applicable'
	is_timberlog=''
	timber_log = Timberlogdetails.objects.filter(appform_id=app_id)
	if timber_log:
		timber_log=timber_log.values()
	else:
		is_timberlog='N/A'
	# transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
	transit_pass_exist = False
	if groups[0] == "revenue officer" and application_detail[0].verify_office == True:
		transit_pass_exist = True
	elif groups[0] == "deputy range officer" and application_detail[0].depty_range_officer == True:
		transit_pass_exist = True
	elif groups[0] == "forest range officer" and application_detail[0].verify_range_officer == True:
		transit_pass_exist = True
	else:
		pass
	print(transit_pass_exist,'----TP')
	return render(request,"my_app/tigram/userviewapplication.html",{'formtype':'view','applicant':APPLICATION,
		'applications':application_detail,'image_documents':image_document,'groups':groups,
		'transit_pass_exist':transit_pass_exist,'vehicle':vehicle,'timber_log':timber_log,
		'trees_species_list':trees_species_list,'isvehicle':isvehicle,'is_timberlog':is_timberlog})

# @login_required
def application_useredit(request,app_id):

	groups=request.user.groups.values_list('name',flat = True)
	application_detail = Applicationform.objects.filter(id=app_id)
	geospecies_list = Species_geodetails.objects.filter(appform_id=app_id).values_list('species_tree_id',flat=True)
	geospecies = Species_geodetails.objects.filter(appform_id=app_id).values('species_tree_id__name','latitude','longitude')
	print(geospecies_list,'--')
	trees_species_list = TreeSpecies.objects.filter(id__in=list(geospecies_list),is_noc=False).values('name')
	image_document=[]
	if image_documents.objects.filter(app_form_id=app_id).exists():
		image_document = image_documents.objects.filter(app_form_id=app_id)[0]
	# if application_detail:
	vehicle = Vehicle_detials.objects.filter(app_form_id=app_id)
	isvehicle=''
	if vehicle:
		vehicle=vehicle[0]
	else:
		isvehicle = 'Not Applicable'
	is_timberlog=''
	timber_log = Timberlogdetails.objects.filter(appform_id=app_id)
	if timber_log:
		timber_log=timber_log.values()
	else:
		is_timberlog='N/A'
	# transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
	transit_pass_exist = False
	# if groups[0] == "revenue officer" and application_detail[0].verify_office == True:
	# 	transit_pass_exist = True
	# elif groups[0] == "deputy range officer" and application_detail[0].depty_range_officer == True:
	# 	transit_pass_exist = True
	# elif groups[0] == "forest range officer" and application_detail[0].verify_range_officer == True:
	# 	transit_pass_exist = True
	# else:
	# 	pass
	is_edit=True if application_detail[0].verify_deputy2==True and application_detail[0].depty_range_officer == False else False

	print(transit_pass_exist,'----TP')
	return render(request,"my_app/tigram/user_editapplication.html",{'formtype':'view','applicant':APPLICATION,
		'applications':application_detail,'image_documents':image_document,'groups':groups,'is_edit':is_edit,
		'transit_pass_exist':transit_pass_exist,'vehicle':vehicle,'timber_log':timber_log,'geospecies':geospecies,
		'trees_species_list':trees_species_list,'isvehicle':isvehicle,'is_timberlog':is_timberlog})

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('edit_application')
def edit_application(request,app_id):
	groups=request.user.groups.values_list('name',flat = True)
	application_detail = Applicationform.objects.filter(id=app_id)
	trees_species_list = TreeSpecies.objects.all().values('name')
	image_document = image_documents.objects.filter(app_form_id=app_id)[0]
	vehicle = Vehicle_detials.objects.filter(app_form_id=app_id)
	isvehicle=''
	if vehicle:
		vehicle=vehicle[0]
	else:
		isvehicle = 'Not Applicable'
	is_timberlog=''
	timber_log = Timberlogdetails.objects.filter(appform_id=app_id)
	if timber_log:
		timber_log=timber_log.values()
	else:
		is_timberlog='N/A'
	# transit_pass_exist = TransitPass.objects.filter(app_form_id=app_id).exists()
	transit_pass_exist = False
	if groups[0] == "revenue officer" and application_detail[0].verify_office == True:
		transit_pass_exist = True
	elif groups[0] == "deputy range officer" and application_detail[0].depty_range_officer == True:
		transit_pass_exist = True
	elif groups[0] == "forest range officer" and application_detail[0].verify_range_officer == True:
		transit_pass_exist = True
	else:
		pass
	print(transit_pass_exist,'----TP')
	return render(request,"my_app/tigram/viewapplication.html",{'formtype':'edit','applicant':APPLICATION,
		'applications':application_detail,'image_documents':image_document,'groups':groups,
		'transit_pass_exist':transit_pass_exist,'vehicle':vehicle,'timber_log':timber_log,
		'trees_species_list':trees_species_list,'isvehicle':isvehicle,'is_timberlog':is_timberlog
		})

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('approve_transit_pass')
def approve_transit_pass(request,app_id):
	application_detail = Applicationform.objects.filter(id=app_id)
	groups=request.user.groups.values_list('name',flat = True)
	reason = request.POST.get('reason')
	if application_detail:
		if application_detail[0].application_status=='R':
			return JsonResponse({'message':'Action cannot be taken, Once Application rejected!'})
	else:
		return JsonResponse({'message':'Bad Request!'})
	if request.POST.get('type') == 'REJECT':
		print(reason,'--reason')

		if groups[0] == "revenue officer":
			application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
      disapproved_by=request.user.id,disapproved_by_grp="By Revenue Officer",

				application_status='R',verify_office = True,verify_office_date = date.today())

		elif groups[0] == "deputy range officer":
			# application_detail = Applicationform.objects.filter(id=app_id)

			if application_detail[0].verify_office==True:
				if Applicationform.objects.filter(id=app_id,is_form_two=True).exists():
					if Applicationform.objects.filter(id=app_id,is_form_two=True,application_status='SA').exists():
						application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
	        		disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
							application_status='R',verify_deputy2 = True,deputy2_date = date.today())
					else:
						application_form = Applicationform.objects.filter(id=app_id).update(disapproved_reason=reason,
	        		disapproved_by=request.user.id,disapproved_by_grp="By Deputy Officer",
							application_status='R',depty_range_officer = True,deputy_officer_date = date.today())
				else:
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

		reason=request.POST.get('reason')
		if groups[0] == "revenue officer":
			application_detail.update(
			reason_office = reason ,
			application_status = 'P',
			#approved_by = request.user,
			approved_by_revenue = request.user,
			verify_office = True,
			verify_office_date = date.today(),
			# transit_pass_id=transit_pass.id,
			# transit_pass_created_date = datetime.date.today(),
			)
		elif groups[0] == "deputy range officer":
			if application_detail[0].verify_office==True:
				if application_detail[0].is_form_two==True:
					if application_detail[0].verify_deputy2==False:
						application_detail.update(
						reason_deputy2 = reason ,
						application_status = 'P',
						approved_by_deputy2 = request.user,
						verify_deputy2 = True,
						deputy2_date = date.today())
					else:
						application_detail.update(
						reason_depty_ranger_office = reason ,
						application_status = 'P',
						approved_by_deputy = request.user,
						depty_range_officer = True,
						deputy_officer_date = date.today(),
						)
				else:
					application_detail.update(
					reason_depty_ranger_office = reason ,
					application_status = 'P',
					approved_by_deputy = request.user,
					depty_range_officer = True,
					deputy_officer_date = date.today(),

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
	# return render(request,"my_app/tigram/application_details.html",{'applicant':APPLICATION,'applications':application_detail})

# import datetime
@login_required
# @group_required('revenue officer','deputy range officer','forest range officer','user')
@group_permissions('check_status')
def check_status(request):
	from datetime import date
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	context['group'] = groups
	# application = Applicationform.objects.filter(by_user_id=request.user.id,is_noc=False,is_form_two=False).order_by('-id')
	application = Applicationform.objects.filter(by_user_id=request.user.id,is_noc=False).order_by('-id')
	tp = TransitPass.objects.filter(app_form__by_user_id=request.user.id).order_by('-app_form_id')
	incr=1
	applicant=[]
	tp_list = []
	for each in application:
		checkstatus = {}
		checkstatus['sr'] =incr
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['created_date'] = each.created_date
		checkstatus['application_status'] = each.get_application_status_display()
		# checkstatus['remark'] = each.reason_range_officer
		checkstatus['tp_issue_date'] = 'Not Generated' if each.application_status != 'A' else each.transit_pass_created_date
		if each.reason_division_officer != '':
			checkstatus['remark'] =  each.reason_division_officer
			checkstatus['remark_date']= each.division_officer_date
		elif each.reason_range_officer != '':
			checkstatus['remark'] =  each.reason_range_officer
			checkstatus['remark_date']= each.range_officer_date
		elif each.reason_depty_ranger_office != '':
			checkstatus['remark'] =  each.reason_depty_ranger_office
			checkstatus['remark_date']= each.deputy_officer_date
		elif each.reason_office != '':
			checkstatus['remark'] =  each.reason_office
			checkstatus['remark_date']= each.verify_office_date
		else:
			checkstatus['remark'] =  'N/A'
			checkstatus['remark_date']= 'N/A'
		if each.application_status == 'R' :
			checkstatus['remark'] = each.disapproved_reason
		checkstatus['query'] = ''
		checkstatus['is_form_two'] =each.is_form_two
		# checkstatus['tp_days'] = 'Not Generated' if each.application_status != 'A' else (datetime.date.today()-each.transit_pass_created_date).days
		if each.application_status != 'A':
			checkstatus['tp_days'] = 'Not Generated'
			checkstatus['verification_status'] =each.get_application_status_display()
		else:
			days_left=7-(date.today()-each.transit_pass_created_date).days
			if days_left<1:
				checkstatus['tp_days'] = 0 #'TransitPass Expired'
				checkstatus['verification_status'] ='TransitPass Expired'
			else:
				checkstatus['tp_days'] = days_left
				checkstatus['verification_status'] =each.get_application_status_display()
		if each.application_status != 'A':
			checkstatus['expiry_date'] = 'Not Generated'
		else:
			print(type(each.transit_pass_created_date))
			date_1 = datetime.strptime(str(each.transit_pass_created_date), "%Y-%m-%d")
			checkstatus['expiry_date'] = date_1 + timedelta(days=7)
		checkstatus['tp_number'] = 'Not Generated' if each.application_status != 'A' else each.transit_pass_id
		checkstatus['edit_log'] =False
		if each.division_officer == True:
			checkstatus['current_status'] =  'Rejected by Division Officer' if each.application_status == 'R' else 'Approved by Division Officer'
			checkstatus['current_status_by'] ='division officer'
		elif each.verify_range_officer == True:
			if each.other_state==False:
				checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer'
				checkstatus['current_status_by'] ='forest range officer'
			else:
				checkstatus['current_status'] =  'Rejected by Forest Range Officer' if each.application_status == 'R' else 'Approved by Forest Range Officer and Division Officer Approval Pending'
				checkstatus['current_status_by'] ='forest range officer'
		elif each.depty_range_officer == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer'  if each.application_status == 'R' else 'Approved by Deputy Range Officer and Forest Range Officer Approval Pending'
			checkstatus['current_status_by'] ='deputy range officer'
		elif each.verify_deputy2 == True :
			checkstatus['current_status'] =  'Rejected by Deputy Range Officer at Stage 1'  if each.application_status == 'R' else 'Approved by Deputy Range Officer at Stage 1 and Deputy Range Officer Approval Pending at Stage 2'
			checkstatus['current_status_by'] ='deputy range officer'
			checkstatus['edit_log'] =True if each.application_status != 'R' else False
		elif each.verify_office == True  :
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Approved by Revenue Officer and Deputy Range Officer Approval Pending'
			checkstatus['current_status_by'] ='revenue officer'
		else:
			checkstatus['current_status'] = 'Rejected by Revenue Officer' if each.application_status == 'R' else 'Revenue Officer Approval Pending'
		applicant.append(checkstatus)
		incr = incr+1
		# checkstatus[incr]=applicant
	noc_application = Applicationform.objects.filter(by_user_id=request.user.id,is_noc=True).order_by('-id')
	incr1=1
	noc_applicant=[]
	for each in noc_application:
		checkstatus = {}
		checkstatus['sr'] =incr
		checkstatus['applicant_no'] = each.id
		checkstatus['application_no'] = each.application_no
		checkstatus['created_date'] = each.created_date
		noc_applicant.append(checkstatus)
		incr1 = incr1+1

	return render(request,"my_app/tigram/checkstatus.html",{'application':applicant,'noc_application':noc_applicant,'groups':context['group']})

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

@login_required
@group_required('revenue officer','deputy range officer','forest range officer')
# @group_permissions()
def disapprove_transit_pass(request,app_id):
	reason = request.POST.get('reason')
	application_detail = Applicationform.objects.filter(id=app_id).update(reason_range_officer=reason,application_status='R')

	return render(request,"my_app/tigram/application_details.html",{'applicant'})

def generate_pdf(src,name):
	pdf = pdfkit.from_url(src, False)
	response = HttpResponse(pdf,content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename='+name+'.pdf'
	return response

@login_required
def user_report12(request,applicant_no):
	logo1=settings.DEFAULT_LOGO
	logo2 = settings.DEFAULT_LOGO
	groups=request.user.groups.values_list('name',flat = True)
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
	# pdf = pdfkit.from_string(wt, False,configuration=config)
	template =''
	if groups[0] in ['revenue officer','deputy range officer','forest range officer']:
		template = get_template("pdf_template/report.html")
	else:
		template = get_template("pdf_template/userreport.html")
	application = Applicationform.objects.filter(id=applicant_no).values()
	# print(application)
	if application:
		context = {'application':application,"logo1":logo1,"logo2":logo2,
		'qr_img':qr_img,'transitpass':transitpass,'is_transitpass':is_transitpass}  # data is the context data that is sent to the html file to render the output.
		html = template.render(context)  # Renders the template with the context data.
		pdf = pdfkit.from_string(html, False)
		# pdf = pdfkit.from_string(html, False, configuration=config)
		# pdf = open("summaryreport.pdf")
		response = HttpResponse(pdf, content_type='application/pdf')  # Generates the response as pdf response.
		response['Content-Disposition'] = 'attachment; filename=UserReport.pdf'
		# pdf.close()
		# os.remove("summaryreport.pdf")  # remove the locally created pdf file.
		return response
	else:
		# message = "No Data Found"
		print('No Data in Summary')
		return HttpResponseRedirect(reverse('officer_dashboard'))


@login_required
@group_permissions('update_timberlog')
def update_timberlog(request,applicant_no):
	application =applicant_no# request.POST.get('app_form_id')
	log_id = request.POST.getlist('log_id[]')
	species = request.POST.getlist('update-species[]')
	length = request.POST.getlist('update-length[]')
	breadth = request.POST.getlist('update-breadth[]')
	volume = request.POST.getlist('update-volume[]')
	latitude = request.POST.getlist('update-latitude[]')
	longitude = request.POST.getlist('update-longitude[]')
	if request.user.is_authenticated:
		groups=request.user.groups.values_list('name',flat = True)
		if groups[0] == 'user':
			Applicationform.objects.filter(id=applicant_no).update(appsecond_two_date=date.today())
		# print(groups[0],'---===')
	tlog_exist = Timberlogdetails.objects.filter(appform=application)
	if tlog_exist:
		tlog_exist.delete()
	tlog=[]
	print(length,"--------",species)
	if len(species) >0 :
		for i in range(len(species)):
			timber = Timberlogdetails(appform_id=application,species_of_tree=species[i],
			length=length[i],volume=volume[i], breadth=breadth[i],
			latitude=latitude[i],longitude=longitude[i])
			tlog.append(timber)
		Timberlogdetails.objects.bulk_create(tlog)
	timber_log=Timberlogdetails.objects.filter(appform_id=applicant_no).values()
		# application.save()
	return JsonResponse({'message':'Updated successfully!!!','timber_log':list(timber_log)})

@login_required
def load_timberlog(request,applicant_no):
	timber_log=Timberlogdetails.objects.filter(appform_id=applicant_no).values()
	return render(request,'my_app/tigram/timber_log_template.html',{'timber_log':timber_log})


def index(request):
	context={}
	if request.user.is_authenticated:
		groups=request.user.groups.values_list('name',flat = True)
		# user= CustomUser.objects.filter(id=request.user.id)
		print(groups)
		context['group'] = groups
	# context['no_of_tp'] = TransitPass.objects.all().count()
	# context['no_of_tp'] = Applicationform.objects.exclude(transit_pass_id__exact='').count()
	context['no_of_app']=Applicationform.objects.all().count()
	context['no_of_tp'] = Applicationform.objects.all().exclude(transit_pass_id=0).count()
	context['no_of_tp_pending'] = Applicationform.objects.filter(Q(application_status='S')|Q(application_status='P')).exclude(~Q(transit_pass_id=0)).count()
	context['no_of_tp_rejected'] = Applicationform.objects.filter(application_status='R').count()
	return render(request,"my_app/tigram/index.html",context)

import json
@login_required
@group_permissions('edit_profile')
def edit_profile(request,user_id):
	context={}
	count = {}

	count['no_of_app']=Applicationform.objects.all().count()
	count['no_of_tp'] = TransitPass.objects.all().count()
	count['no_of_tp_pending'] = Applicationform.objects.filter(Q(application_status='S')|Q(application_status='P')).count()
	count['no_of_tp_rejected'] = Applicationform.objects.filter(application_status='R').count()
	groups=request.user.groups.values_list('name',flat = True)
	user= CustomUser.objects.filter(id=user_id)
	context['group'] = groups
	if request.method == "POST" or request.is_ajax():
		# print(request.data,'------------AJAX______')
		contact = request.POST.get("contact")
		email = request.POST.get("email")
		name = request.POST.get("name")
		address = request.POST.get("address")
		profile_photo =request.FILES.get('profile_photo',None)
		# print(request.body.profile_photo)
		# print(request.POST)
		# print(contact,'------------')
		print(profile_photo,'---pp')
		url = 'media/upload/profile/'
		profile_pic=''
		if CustomUser.objects.filter(phone = contact).exclude(id=user_id).exists():
			return JsonResponse({'message':'Profile Details not updated','status':'400','pic_url':profile_pic,'msg':'Contact already exist!'})
		if profile_photo is None:
			# profile_pic = upload_product_image_file(user_id,profile_photo,url,'Profile')
			# print(profile_pic,'------')
			user_update= user.update(
				phone = contact,
				name=name,
				address=address,
				# email= email,
				)
		else:
			profile_pic = upload_product_image_file(user_id,profile_photo,url,'Profile')
			print(profile_pic,'------')
			user_update= user.update(
				phone = contact,
				name=name,
				address=address,
				profile_pic = profile_pic
				# email= email,
				)
		user=user[0]

		# return render(request,"my_app/tigram/editprofile.html",{'user':user,'updated':user_update,'groups':context['group'],'count':count})
		# return render(request,"my_app/tigram/profile.html",{'user':user,'updated':user_update,'groups':context['group'],'count':count})
		return JsonResponse({'message':'Updated successfully','status':'200','pic_url':profile_pic})
	else :
		user=user[0]
		pass
	# return render(request,"my_app/tigram/editprofile.html",{'user':user,'groups':context['group'],'count':count})
	return render(request,"my_app/tigram/profile.html",{'user':user,'groups':context['group'],'count':count})


@login_required
@group_permissions('view_profile')
def view_profile(request,user_id):
	context={}
	count = {}
	count['no_of_app']=Applicationform.objects.all().count()
	count['no_of_tp'] = TransitPass.objects.all().count()
	count['no_of_tp_pending'] = Applicationform.objects.filter(Q(application_status='S')|Q(application_status='P')).count()
	count['no_of_tp_rejected'] = Applicationform.objects.filter(application_status='R').count()
	groups=request.user.groups.values_list('name',flat = True)
	context['group'] = groups

	user= CustomUser.objects.filter(id=user_id)[0]
	return render(request,"my_app/tigram/profile.html",{'user':user,'groups':context['group'],'count':count})
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
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from xhtml2pdf import pisa
# from io import StringIO
from django.template.loader import get_template
from django.template import Context
def transit_pass_pdf2(request,applicant_no):
	logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	logo2 = settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
	transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
	log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
	signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
	qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
	main_url=settings.SERVER_BASE_URL

	print(applicant_no,"******************")
	application = Applicationform.objects.filter(id=applicant_no).values()
	print(application)
	# if application:
	context = {'applications':application,"logo1":logo1,"logo2":logo2,
		'signature_img':signature_img,'qr_img':qr_img,
		'transitpass':transitpass,'log_details':log_details}
	pdf = render_to_pdf('pdf_template/transitpass.html',context)
		# return HttpResponse(result.getvalue(), content_type='application/pdf')
	response = HttpResponse(pdf, content_type='application/pdf')
	filename = "TransitPass.pdf"
	content = "attachment; filename='%s'" %(filename)
	response['Content-Disposition'] = content
	return response
	# response = HttpResponse(pdf, content_type='application/pdf')
	# filename = "Invoice_%s.pdf" %("12341231")
	# content = "attachment; filename='%s'" %(filename)
	# response['Content-Disposition'] = content
	# return response
@login_required
@group_permissions('transit_pass_pdf')
def transit_pass_pdf(request,applicant_no):
	# logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	# logo2 = settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
	logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
	logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
  # image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
	# transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
	# log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
	# signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
	# qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)

	print(applicant_no,"******************")
	application = Applicationform.objects.filter(id=applicant_no)
	print(application)
	is_vehicle = "NO"
	vdata = {}
	if application:
		if application[0].other_state == False:
			authorizer_name = application[0].approved_by.name if application[0].is_noc==False and application[0].deemed_approval==False else 'N/A'
		else:
			authorizer_name = application[0].approved_by_division.name if application[0].is_noc==False and application[0].deemed_approval==False else 'N/A'
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
		# date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		date_1 = datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		main_url=settings.SERVER_BASE_URL+'static/media/qr_code/'
		# print(application[0]['approved_by_id__name'])\
		# <td style="width :300px !important; text-align: center;font-size: 16px">{{each.species_of_tree}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.length}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.breadth}}</td>
  #         <td style="text-align: center;font-size: 16px">{{each.volume}}</td>
		log={}
		# print(log_details.values(),'----')
		# for each in log_details:
		# 	each['main_url'] = main_url+each['log_qr_code_img']
			# log['']=
			# log['']=
			# log['']=
			# log['']=

		print(log_details,'------=')
		# expiry_date = date_1 + datetime.timedelta(days=7)
		expiry_date = date_1 + timedelta(days=7)
		context = {'application':application,"logo1":logo1,"logo2":logo2,"logo3":logo3,'main_url':main_url,
			'signature_img':signature_img,'qr_img':qr_img,'authorizer_name':authorizer_name,"is_vehicle":is_vehicle,"vdata":vdata,
			'transitpass':transitpass,'log_details':log_details,'expiry_date':expiry_date}
		# context = {'application':application,"logo1":logo1,"logo2":logo2,
		# 	'signature_img':signature_img,'qr_img':qr_img,
		# 	'transitpass':transitpass,'log_details':log_details}
		# Create a Django response object, and specify content_type as pdf
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
		if pisa_status.err:
			return HttpResponse('We had some errors <pre>' + html + '</pre>')
		return response
	else:
		print('No Data in Summary')
		return HttpResponseRedirect(reverse('dashboard'))


def get_log_qr_details(request,app_id):
	application = Applicationform.objects.filter(id=app_id)
	print(application)
	if application:
		authorizer_name = application[0].approved_by.name
		application=application.values()

		transitpass = TransitPass.objects.filter(app_form_id=app_id).values()
		log_details = Timberlogdetails.objects.filter(appform_id=app_id).values()
		# signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)

		# qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)

		# date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		# date_1 = datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		main_url = settings.SERVER_BASE_URL+"""static/media/qr_code/"""
		# print(application[0]['approved_by_id__name'])
		# print(main_url,log_details[0].log_qr_code)
		req_url=request.META['HTTP_HOST']
		print(req_url,"-----HOST")
		# expiry_date = date_1 + datetime.timedelta(days=7)
		# expiry_date = date_1 + timedelta(days=7)
		context = {"req_url":req_url,
			'transitpass':list(transitpass),'log_details':list(log_details)}
		return JsonResponse(context,safe=False)


@login_required
@group_permissions('log_qrcode_pdf')
def log_qrcode_pdf(request,log_no):
	# logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
  #logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.jpg"
	logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
	logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
	log_details = Timberlogdetails.objects.filter(id=log_no)
	if log_details:
		print(log_details,'---------')
		# authorizer_name = log_details[0].approved_by.name
		# log_details=log_details.values()
		# log_code=

		# signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
		# qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
		# date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		# date_1 = datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		# qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(log_details[0].log_qr_code_img)
		# qr_img = "http://localhost:8000/"+"""static/media/qr_code/"""+ str(log_details[0].log_qr_code_img)
		qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(log_details[0].log_qr_code_img)

		main_url = settings.SERVER_BASE_URL+"""static/media/qr_code/"""
		# print(application[0]['approved_by_id__name'])
		# print(main_url,log_details[0].log_qr_code)
		req_url=request.META['HTTP_HOST']
		print(req_url,"-----HOST")
		# expiry_date = date_1 + datetime.timedelta(days=7)
		# expiry_date = date_1 + timedelta(days=7)
		context = {'log_details':log_details[0],"logo1":logo1,"logo2":logo2,"logo3":logo3,
		"qr_img":qr_img,"req_url":req_url}

		response = HttpResponse(content_type='application/pdf')
		today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
		# print(today_stamp,'======',datetime.now())
		filename= 'Log_Details-'+str(log_details[0].appform.application_no)+'-'+today_stamp+''
		response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
		# find the template and render it.
		template = get_template('pdf_template/log_qr_details.html')
		html = template.render(context)

		# create a pdf
		pisa_status = pisa.CreatePDF(
			html, dest=response, link_callback=link_callback)
		# if error then show some funy view
		if pisa_status.err:
			return HttpResponse('We had some errors <pre>' + html + '</pre>')
		return response
	else:
		print('No Data in QR')
		return HttpResponseRedirect(reverse('dashboard'))

@login_required
@group_permissions('qr_code_pdf')
def qr_code_pdf(request,applicant_no):
	# logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
	logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
	logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
  #logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.jpg"
	# image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
	# transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
	# log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
	# signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
	# qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)

	print(applicant_no,"******************")
	application = Applicationform.objects.filter(id=applicant_no)
	print(application)
	if application:
		authorizer_name = application[0].approved_by.name
		application=application.values()

		transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
		log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
		# signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
		qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
		# date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		date_1 = datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		main_url = settings.SERVER_BASE_URL+'static/media/qr_code/'
		# print(application[0]['approved_by_id__name'])
		# print(main_url,log_details[0].log_qr_code)
		req_url=request.META['HTTP_HOST']
		print(req_url,"-----HOST")
		# expiry_date = date_1 + datetime.timedelta(days=7)
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
			return HttpResponse('We had some errors <pre>' + html + '</pre>')
		return response
	else:
		print('No Data in Summary')
		return HttpResponseRedirect(reverse('dashboard'))

@login_required
@group_permissions('user_report')
def user_report(request,applicant_no):
	# logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"

	logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
	logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
  #logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.jpg"
	groups=request.user.groups.values_list('name',flat = True)
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
	if groups[0] in ['revenue officer','deputy range officer','forest range officer']:
		template = get_template("pdf_template/newreport.html")
	else:
		template = get_template("pdf_template/newreport.html")
	application = Applicationform.objects.filter(id=applicant_no).values()
	# print(application)
	if application:
		approved_names = Applicationform.objects.filter(id=applicant_no).values('approved_by_division__name','approved_by_deputy__name','approved_by_revenue__name','approved_by__name')
		# date_1 = datetime.datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		# expiry_date = date_1 + datetime.timedelta(days=7)
		date_1 = datetime.strptime(str(application[0]['transit_pass_created_date']), "%Y-%m-%d")
		expiry_date = date_1 + timedelta(days=7)
		context = {'application':application,"logo1":logo1,"logo2":logo2,"logo3":logo3,'expiry_date':expiry_date,
		'qr_img':qr_img,'transitpass':transitpass,'is_transitpass':is_transitpass,'approved_names':list(approved_names)}  # data is the context data that is sent to the html file to render the output.
		response = HttpResponse(content_type='application/pdf')
		# response['Content-Disposition'] = 'attachment; filename="UserReport.pdf"'
		today_stamp= str(datetime.now()).replace(' ','').replace(':','').replace('.','').replace('-','')
		# print(today_stamp,'======',datetime.now())
		filename= 'UserReport-'+str(application[0]['application_no'])+'-'+today_stamp+''
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
	else:
		print('No Data in Summary')
		return HttpResponseRedirect(reverse('dashboard'))

# http://127.0.0.1:8000
@login_required
def transit_pass_pdf1(request,applicant_no):
	logo1=settings.DEFAULT_LOGO
	logo2 = settings.DEFAULT_LOGO
	# config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
	# config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
	# pdf = pdfkit.from_string(wt, False,configuration=config)
	template = get_template("pdf_template/transitpass.html")
	# css = os.path.join(settings.STATIC_URL, 'css/summaryreport.css', 'summaryreport.css')
	# applications = Applicationform.objects.all().order_by('-id')
	application = Applicationform.objects.filter(id=applicant_no)
	# print(application)
	if application:
		application=application.values()
		image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
		transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
		log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
		signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
		qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
		date_1 = datetime.datetime.strptime(str(application[0].transit_pass_created_date), "%Y-%m-%d")
		expiry_date = date_1 + datetime.timedelta(days=7)
		context = {'application':application,"logo1":logo1,"logo2":logo2,
			'signature_img':signature_img,'qr_img':qr_img,
			'transitpass':transitpass,'log_details':log_details,'expiry_date':expiry_date}  # data is the context data that is sent to the html file to render the output.
		html = template.render(context)  # Renders the template with the context data.
		pdf = pdfkit.from_string(html, False)
		# pdf = pdfkit.from_string(html, False, configuration=config)
		# pdf = open("summaryreport.pdf")
		response = HttpResponse(pdf, content_type='application/pdf')  # Generates the response as pdf response.
		response['Content-Disposition'] = 'attachment; filename=transitpass.pdf'
		# pdf.close()
		# os.remove("summaryreport.pdf")  # remove the locally created pdf file.
		return response
	else:
		# message = "No Data Found"
		print('No Data in Summary')
		return HttpResponseRedirect(reverse('officer_dashboard'))

@login_required
def transit_pass_pdf2(request,applicant_no):
	logo1=settings.DEFAULT_LOGO
	logo2 = settings.DEFAULT_LOGO
	# config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
	# config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
	# pdf = pdfkit.from_string(wt, False,configuration=config)
	template = get_template("pdf_template/transitpass.html")
	# css = os.path.join(settings.STATIC_URL, 'css/summaryreport.css', 'summaryreport.css')
	# applications = Applicationform.objects.all().order_by('-id')
	application = Applicationform.objects.filter(id=applicant_no).values()
	# print(application)
	if application:
		image_document = image_documents.objects.filter(app_form_id=applicant_no)[0]
		transitpass = TransitPass.objects.filter(app_form_id=applicant_no)[0]
		log_details = Timberlogdetails.objects.filter(appform_id=applicant_no)
		signature_img = settings.SERVER_BASE_URL+"""static/media/upload/signature/"""+ str(image_document.signature_img)
		qr_img = settings.SERVER_BASE_URL+"""static/media/qr_code/"""+ str(transitpass.qr_code_img)
		context = {'application':application,"logo1":logo1,"logo2":logo2,
			'signature_img':signature_img,'qr_img':qr_img,
			'transitpass':transitpass,'log_details':log_details}  # data is the context data that is sent to the html file to render the output.
		html = template.render(context)  # Renders the template with the context data.
		pdf = pdfkit.from_string(html, False)
		# pdf = pdfkit.from_string(html, False, configuration=config)
		# pdf = open("summaryreport.pdf")
		response = HttpResponse(pdf, content_type='application/pdf')  # Generates the response as pdf response.
		response['Content-Disposition'] = 'attachment; filename=transitpass.pdf'
		# pdf.close()
		# os.remove("summaryreport.pdf")  # remove the locally created pdf file.
		return response
	else:
		# message = "No Data Found"
		print('No Data in Summary')
		return HttpResponseRedirect(reverse('officer_dashboard'))


@login_required
@group_required('revenue officer','deputy range officer','forest range officer')
def view_summary_report(request):
	applications = Applicationform.objects.all().order_by('-id')


	return render(request,"my_app/tigram/summaryreport.html",{'applications':applications})

def load_division(request):
	range_area = request.GET.get('area_range')
	print(range_area)
	# div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	if range_area.isdigit():
		div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	else:
			div_list = list(Range.objects.filter(name__iexact=range_area).values('division_id__name'))
	# div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	return JsonResponse({'div_list':div_list})

def load_taluka(request):
	dist = request.GET.get('dist')
	print(dist)
	# div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	if dist.isdigit():
		div_list = list(Taluka.objects.filter(dist_id=dist).values('taluka_name'))
	else:
			div_list = list(Taluka.objects.filter(dist__district_name__iexact=dist).values('taluka_name'))
	# div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	return JsonResponse({'div_list':div_list})


def load_village(request):
	taluka = request.GET.get('taluka')
	print(taluka)
	# div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	if taluka.isdigit():
		div_list = list(Village.objects.filter(taluka_id=taluka).values('village_name'))
	else:
			div_list = list(Village.objects.filter(taluka__taluka_name__iexact=taluka).values('village_name'))
	# div_list = list(Range.objects.filter(id=range_area).values('division_id'))
	return JsonResponse({'div_list':div_list})

@group_permissions('role_permission_list')
def role_permission_list(request):
	# role_permission_list = RolePermission.objects.all()
	role_permission_list = RoleMethod.objects.filter().values()
	# role_list = Group.objects.values('name','id')
	# role_list = Group.objects.values('name')
	role_list = Group.objects.values('name','id').filter(is_delete=False)
	parent_data=[]
	parent_data=[]
	rlist=list(role_permission_list)
	# print(rlist,'-===-=')
	for keys in rlist:
		if keys['parent_id'] is None:
			keys['childs']=[]
			parent_data.append(keys)

	for keys in rlist:
		for key in parent_data:
			if key['id'] == keys['parent_id']:
				key['childs'].append(keys)
	print(parent_data,'-------')
	# role_permission_list =
	return render(request,"my_app/tigram/admin/all_permissions.html",{'role_list':role_list,'permissions1':list(role_permission_list),'permissions':parent_data,'menu':'permissions'})

@group_permissions('save_role_permission')
def save_role_permission(request):
	permissions_list = request.POST.getlist('perm_list[]')
	group_id = request.POST.get('group')
	print(group_id,'-----')
	role_perm=[]
	RolePermission.objects.filter(group_id=group_id).delete()
	for each in permissions_list:
		each_role_perm = RolePermission(method_id=each,group_id=group_id,created_by_id=request.user.id)
		role_perm.append(each_role_perm)
	RolePermission.objects.bulk_create(role_perm)
	return JsonResponse({'message':'Added successfully!'})

@group_permissions('view_role_permission')
def view_role_permission(request,role_id):
	# permissions_list = request.POST.getlist('perm_list[]')
	# group_id = request.POST.get('group')
	# print(group_id,'-----')
	# role_perm=[]
	permissions = RolePermission.objects.filter(group_id=role_id).values_list('method_id',flat=True)
	print(permissions)
	# RolePermission.objects.filter(group_id=group_id).delete()
	# for each in permissions_list:
	# 	each_role_perm = RolePermission(method_id=each,group_id=group_id,created_by_id=request.user.id)
	# 	role_perm.append(each_role_perm)
	# RolePermission.objects.bulk_create(role_perm)
	return JsonResponse({'permissions':list(permissions)})
	# return render(request)

@group_permissions('edit_role_permission')
def edit_role_permission(request,role_id):
	# role_permission_list = RolePermission.objects.all()
	role_permission_list = RoleMethod.objects.all().values()
	parent_list = RoleMethod.objects.filter(types='parent').values('id')
	print(parent_list)
	role_list = Group.objects.values('name','id')
	rlist=list(role_permission_list)
	# print(rlist,'-===-=')
	parent_data=[]
	for keys in rlist:
		if keys['parent_id'] is None:
			keys['childs']=[]
			parent_data.append(keys)

	for keys in rlist:
		for key in parent_data:
			if key['id'] == keys['parent_id']:
				key['childs'].append(keys)
	print(parent_data,'-------')
	# role_permission_list =
	return render(request,"my_app/tigram/admin/all_permissions.html",{'selected_role':role_id,'role_list':role_list,'parent_list':list(parent_list),'permissions2':role_permission_list,'permissions':parent_data,'menu':'permissions'})

# @group_permissions('admin_dashboard')
def admin_dashboard(request):
	context={}
	context['active_users_no'] = CustomUser.objects.filter(groups__name__in=['user'],is_delete=False).count()
	context['application_no'] = Applicationform.objects.all().count()
	#context['application_no'] = CustomUser.objects.filter(groups__name__in=['user','deputy range officer','forest range officer','division officer','revenue officer'],is_delete=False).count()
	context['officer_no'] = CustomUser.objects.filter(groups__name__in=['deputy range officer','forest range officer','division officer','field officer','state officer'],is_delete=False).count()
	context['div_no'] = Division.objects.filter(is_delete=False).count()
	context['range_no'] = Range.objects.filter(is_delete=False).count()
	context['revenue_no'] = CustomUser.objects.filter(groups__name='revenue officer',is_delete=False).count()
	cs_user = CustomUser.objects.all().values_list('id',flat=True)
	cs_group = Group.objects.all().values_list('user',flat=True)

	print(set(cs_user) - set(cs_group),'---------=')

	context['no_of_app']=Applicationform.objects.all().count()
	context['no_of_tp'] = TransitPass.objects.all().count()
	context['no_of_tp_pending'] = Applicationform.objects.filter(Q(application_status='S')|Q(application_status='P')).count()
	context['no_of_tp_rejected'] = Applicationform.objects.filter(application_status='R').count()

	return render(request,"my_app/tigram/admin/dashboard.html",{'context':context,'menu':'dashboard'})



@group_permissions('view_users')
def view_users(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='user')
	#print('USER',proof_list)
	all_users_list=CustomUser.objects.filter(is_delete=False,groups__name='user').values()
	return render(request,"my_app/tigram/admin/user_mange2.html",{'all_users':all_users,'proof_list':proof_list,'menu':'user','all_users_list':list(all_users_list)})

@group_permissions('update_users')
def update_users(request,user_id):
	cust_user = CustomUser.objects.filter(id=user_id)

	if cust_user:
		created_,ctx= update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)

	return JsonResponse({'message':'Updated Successfully!'})


@group_permissions('delete_users')
def delete_users(request):
	message=""
	if request.method =="POST":
		delete_list = request.POST.getlist('delete_list[]')
		# delete_list=delete_list.split(",")
		print(delete_list,'---delete_list')
		is_deleted= CustomUser.objects.filter(id__in=delete_list).update(is_delete=True)
		# is_deleted= CustomUser.objects.filter(id__in=delete_list).delete()
		if is_deleted:
			message = "All selected users deleted!"
			return JsonResponse({'message':message})
	message="No Action Occurred!"
	return JsonResponse({'message':message})

@group_permissions('view_users')
def detail_view_users(request,user_id):
	detail_user=list(CustomUser.objects.filter(id=user_id).values())
	print('USER data',detail_user)
	return JsonResponse({'detail_user':detail_user})

@group_permissions('detail_view_officer')
def detail_view_officer(request,user_id,officer_type):
	rev_detail=[]
	detail_user=list(CustomUser.objects.filter(id=user_id).values())
	if officer_type =='revenue':
		rev_detail=list(RevenueOfficerdetail.objects.filter(Rev_user=user_id).values())
		print('Inside Revenue',rev_detail)
	elif officer_type=="division_officer":
		rev_detail=list(DivisionOfficerdetail.objects.filter(div_user=user_id).values())
		print('Inside Division',rev_detail)
	elif officer_type == 'fod' :
		rev_detail=list(ForestOfficerdetail.objects.filter(fod_user=user_id).values())
		print('Inside FOD',rev_detail)
	elif officer_type == 'deputy':
		rev_detail=list(ForestOfficerdetail.objects.filter(fod_user=user_id).values())
		print('Inside Deputy',rev_detail)
	elif officer_type == 'field':
		rev_detail=list(ForestOfficerdetail.objects.filter(fod_user=user_id).values())
		print('Inside Deputy',rev_detail)
	elif officer_type == 'state':
		rev_detail=list(StateOfficerdetail.objects.filter(state_user_id=user_id).values())
		print('Inside State',rev_detail)
	print('USER DATA',detail_user )
	return JsonResponse({'detail_user':detail_user,'rev_detail':rev_detail})

@group_permissions('delete_user')
def delete_user(request,user_id):
	# detail_user=CustomUser.objects.filter(id=user_id).delete()
	detail_user=CustomUser.objects.filter(id=user_id).update(is_delete=True)
	return JsonResponse({'message':"Successfully Deleted User"})

@group_permissions('view_deputy_officers')
def view_deputy_officers(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='deputy range officer')
	range_areas = Range.objects.filter(is_delete=False).values('name','id')
	div_list = Division.objects.filter(is_delete=False).values('name','id')
	return render(request,"my_app/tigram/admin/all_officer.html",{'all_users':all_users,
				'proof_list':proof_list,'menu':'deputy_officer',
				'range_areas':range_areas,'div_list':div_list})



@group_permissions('add_revenue_officers')
def add_revenue_officers(request):
	photo_proof_name = request.POST.get('photo_proof_select')
	photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='revenue officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	created_,ctx= create_new_user(request,'revenue officer')
	if ctx['response_code'] =="error":
		return JsonResponse(ctx)
	rev_user= RevenueOfficerdetail.objects.create(
		post=post_name,
		office_address=office_address,
		Rev_user=created_,
		range_name_id=range_name,
		division_name_id=division_name
		)
	return JsonResponse({'message':'Created Successfully!'})

@group_permissions('add_forest_range_officers')
def add_forest_range_officers(request):
	photo_proof_name = request.POST.get('photo_proof_select')
	photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='forest range officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	created_,ctx= create_new_user(request,'forest range officer')
	if ctx['response_code'] =="error":
		return JsonResponse(ctx)

	rev_user= ForestOfficerdetail.objects.create(
		post=post_name,
		office_address=office_address,
		fod_user=created_,
		range_name_id=range_name,
		division_name_id=division_name
		)
	return JsonResponse({'message':'Created Successfully!'})

@group_permissions('add_deputy_range_officers')
def add_deputy_range_officers(request):
	photo_proof_name = request.POST.get('photo_proof_select')
	photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='deputy range officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	created_,ctx= create_new_user(request,'deputy range officer')
	if ctx['response_code'] =="error":
		return JsonResponse(ctx)

	rev_user= ForestOfficerdetail.objects.create(
		post=post_name,
		office_address=office_address,
		fod_user=created_,
		range_name_id=range_name,
		division_name_id=division_name
		)
	return JsonResponse({'message':'Created Successfully!'})

#DFO
@group_permissions('view_deputy_officers')
def view_division_officers(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='division officer')
	div_list = Division.objects.filter(is_delete=False).values('name','id')
	return render(request,"my_app/tigram/admin/all_dfo.html",{'all_users':all_users,
				'proof_list':proof_list,'menu':'division_officer',
				'div_list':div_list})
# @group_permissions('add_division_officers')
def add_division_officers(request):
	photo_proof_name = request.POST.get('photo_proof_select')
	photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='division officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	created_,ctx= create_new_user(request,'division officer')
	if ctx['response_code'] =="error":
		return JsonResponse(ctx)

	rev_user= DivisionOfficerdetail.objects.create(
		post=post_name,
		office_address=office_address,
		div_user=created_,
		division_name_id=division_name
		)
	return JsonResponse({'message':'Created Successfully!'})

# @group_permissions('update_division_officers')
def update_division_officers(request,user_id):
	photo_proof_name = request.POST.get('photo_proof_select')
	#photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	# proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='division officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	if all_users:
		created_,ctx = update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)
		DivisionOfficerdetail.objects.filter(div_user_id=user_id).update(post=post_name,
			office_address=office_address,division_name_id=division_name)

	return JsonResponse({'message':'Updated Successfully!'})

#Field Officer
@group_permissions('view_field_officers')
def view_field_officers(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='field officer')
	range_areas = Range.objects.filter(is_delete=False).values('name','id')
	div_list = Division.objects.filter(is_delete=False).values('name','id')
	return render(request,"my_app/tigram/admin/all_officer.html",{'all_users':all_users,
				'proof_list':proof_list,'menu':'field_officer','range_areas':range_areas,
				'div_list':div_list})

@group_permissions('add_field_officers')
def add_field_officers(request):
	photo_proof_name = request.POST.get('photo_proof_select')
	photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='field officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	created_,ctx= create_new_user(request,'field officer')
	if ctx['response_code'] =="error":
		return JsonResponse(ctx)

	rev_user= ForestOfficerdetail.objects.create(
		post=post_name,
		office_address=office_address,
		fod_user=created_,
		range_name_id=range_name,
		division_name_id=division_name
		)
	return JsonResponse({'message':'Created Successfully!'})

@group_permissions('update_field_officers')
def update_field_officers(request,user_id):
	photo_proof_name = request.POST.get('photo_proof_select')
	# photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	# proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='field officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	if all_users:
		# created_= update_users_fun(request,user_id)
		created_,ctx= update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)
		ForestOfficerdetail.objects.filter(fod_user_id=user_id).update(post=post_name,
			office_address=office_address,range_name_id=range_name,division_name_id=division_name)

	return JsonResponse({'message':'Updated Successfully!'})

#State Officer
@group_permissions('view_state_officers')
def view_state_officers(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='state officer')
	#range_areas = Range.objects.filter(is_delete=False).values('name','id')
	#div_list = Division.objects.filter(is_delete=False).values('name','id')
	return render(request,"my_app/tigram/admin/all_state.html",{'all_users':all_users,
				'proof_list':proof_list,'menu':'state_officer'})

@group_permissions('add_state_officers')
def add_state_officers(request):
	print('Inside addition of State')

	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	state_name = request.POST.get('state_name')
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='state officer')

	created_,ctx= create_new_user(request,'state officer')
	if ctx['response_code'] =="error":
		return JsonResponse(ctx)

	rev_user= StateOfficerdetail.objects.create(
		post=post_name,
		office_address=office_address,
		state_user=created_,
		state_name=state_name,
		)
	print('Output',rev_user)
	return JsonResponse({'message':'Created Successfully!'})

@group_permissions('update_state_officers')
def update_state_officers(request,user_id):
	photo_proof_name = request.POST.get('photo_proof_select')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	state_name = request.POST.get('state_name')
	# state_user_id = request.POST.get('state_id')
	proof_list = PhotoProof.objects.all().values()

	all_users=CustomUser.objects.filter(groups__name='state officer')

	if all_users:

		created_,ctx= update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)
		StateOfficerdetail.objects.filter(state_user_id=user_id).update(post=post_name,
			office_address=office_address, state_name = state_name )

	return JsonResponse({'message':'Updated Successfully!'})

def update_users_fun(request,user_id):
	proof_list = PhotoProof.objects.all().values()
	# all_users=CustomUser.objects.filter(groups__name='user')
	# print('update_users---===')
	context={}
	username = request.POST.get('uname')
	email = request.POST.get('email')
	phone = request.POST.get('number')
	passwd = request.POST.get('psw')
	passwd2 = request.POST.get('psw2')
	address = request.POST.get('address')
	photo_proof_no = request.POST.get('photo_proof_no')
	photo_proof_name = request.POST.get('photo_proof_select')
	photo_proof_doc = request.FILES.get('photo_proof')
	#print(passwd,'---',photo_proof_doc)
	print(photo_proof_doc,'----------photo_proof_doc' )

	make_id = str(user_id)+'r'
	url = '/static/media/upload/'
	# print('----here2----')

	if photo_proof_doc!=None:
		saved_photo=upload_product_image_file(make_id,photo_proof_doc,url,'PhotoProof')
		CustomUser.objects.filter(id=user_id).update(photo_proof_img=saved_photo)

	if passwd!=passwd2:
		context['response_code'] = 'error'
		context['message']="Passwords doesnt match!"

	if 'response_code' in context:
		return False,context

	else:
		print('Pass----', passwd)
		if passwd!='':
			new_password = make_password(passwd)
			print(new_password)
			cust_query = CustomUser.objects.filter(id=user_id).update(
				name=username,photo_proof_no=photo_proof_no, password=new_password,
				photo_proof_name=photo_proof_name,address=address)
		else:
	# isuser.update(password=new_password)
			print('HERE---------------')
			cust_query = CustomUser.objects.filter(id=user_id).update(
				name=username,photo_proof_no=photo_proof_no,
				photo_proof_name=photo_proof_name,address=address)

		context['response_code'] = 'success'
		context['message']="Updated successfully!"
		return True,context
	return True,context

@group_permissions('update_deputy_range_officers')
def update_deputy_range_officers(request,user_id):
	photo_proof_name = request.POST.get('photo_proof_select')
	# photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	# proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='deputy range officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	if all_users:
		# created_= update_users_fun(request,user_id)
		created_,ctx= update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)
		ForestOfficerdetail.objects.filter(fod_user_id=user_id).update(post=post_name,
			office_address=office_address,range_name_id=range_name,division_name_id=division_name)

	return JsonResponse({'message':'Updated Successfully!'})


@group_permissions('update_revenue_officers')
def update_revenue_officers(request,user_id):
	photo_proof_name = request.POST.get('photo_proof_select')
	# photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	# proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='revenue officer')

	# revenue = RevenueOfficerdetail.objects.all().values()
	if all_users:
		created_,ctx= update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)
		RevenueOfficerdetail.objects.filter(Rev_user_id=user_id).update(post=post_name,
			office_address=office_address,range_name_id=range_name,division_name_id=division_name)

	return JsonResponse({'message':'Updated Successfully!'})

@group_permissions('update_forest_range_officers')
def update_forest_range_officers(request,user_id):
	photo_proof_name = request.POST.get('photo_proof_select')
	# photo_proof_doc = request.FILES.get('photo_proof')
	office_address = request.POST.get('off_address')
	post_name = request.POST.get('post_name')
	range_name = request.POST.get('range_name')
	division_name = request.POST.get('div_name')

	# proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(groups__name='forest range officer')
	# revenue = RevenueOfficerdetail.objects.all().values()
	if all_users:
		created_,ctx= update_users_fun(request,user_id)
		if ctx['response_code'] =="error":
			return JsonResponse(ctx)
		ForestOfficerdetail.objects.filter(fod_user_id=user_id).update(post=post_name,
			office_address=office_address,range_name_id=range_name,division_name_id=division_name)
	return JsonResponse({'message':'Updated Successfully!'})

@group_permissions('view_revenue_officers')
def view_revenue_officers(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='revenue officer')
	revenue = RevenueOfficerdetail.objects.all().values()
	range_areas = Range.objects.filter(is_delete=False).values('name','id')
	div_list = Division.objects.filter(is_delete=False).values('name','id')
	return render(request,"my_app/tigram/admin/all_officer.html",{'all_users':all_users,
				'proof_list':proof_list,'revenue_list':revenue,'menu':'revenue_officer',
				'range_areas':range_areas,'div_list':div_list})

@group_permissions('view_forest_officers')
def view_forest_officers(request):
	proof_list = PhotoProof.objects.all().values()
	all_users=CustomUser.objects.filter(is_delete=False,groups__name='forest range officer')
	range_areas = Range.objects.filter(is_delete=False).values('name','id')
	div_list = Division.objects.filter(is_delete=False).values('name','id')
	return render(request,"my_app/tigram/admin/all_officer.html",{'all_users':all_users,
				'proof_list':proof_list,'menu':'forest_officer',
				'range_areas':range_areas,'div_list':div_list})

@group_permissions('add_division')
def add_division(request):
	# context={}
	division = request.POST.get('division')
	print('POST division----',division)
	state= request.POST.get('state')
	print('POST STATE----',state)
	state_name = State.objects.filter(id=state).values('name')
	print('STATE NAME------',state_name)
	ranges = Division.objects.create(name=division,state_id = state,created_by_id=request.user.id)
	# messages = "Division added successfully!"
	# context['menu']='forest_officer'
	print('ADDD division----',ranges)
	return JsonResponse({'messages':"Division added successfully!"})

@group_permissions('view_divisions')
def view_divisions(request):
	# context={}
	ranges = Division.objects.filter(is_delete=False).values('name','id','state__name','state_id','created_date')
	state = State.objects.filter(is_delete=False).values('name','id')
	print('ranges----',ranges)
	print('state-----', state)
	# context['ranges'] = list(ranges)
	# return JsonResponse(context)
	return render(request,"my_app/tigram/admin/all_divisions.html",{'ranges':list(ranges),'menu':'divisions','state':list(state)})

@group_permissions('edit_division')
def edit_division(request,div_id):

	div_name = request.POST.get('division')
	state = request.POST.get('state')
	ranges = Division.objects.all().values()
	Division.objects.filter(id=div_id).update(name=div_name,state_id =state)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Division updated successfully!"})

@group_permissions('delete_division')
def delete_division(request,div_id):

	div_name = request.POST.get('div_name')
	Division.objects.filter(id=div_id).filter(is_delete=True)
	Division.objects.filter(id=div_id).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Division deleted successfully!"})

@group_permissions('delete_divisions')
def delete_divisions(request):
	delete_list = request.POST.getlist('delete_list[]')
	print(delete_list,'---list')
	# div_name = request.POST.get('div_name')
	Division.objects.filter(id__in=delete_list).update(is_delete=True)
	Range.objects.filter(division_id__in=delete_list).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Selected Divisions have been deleted successfully!"})

#@group_permissions('view_species')
def view_tree_species(request):
	# context={}
	ranges = TreeSpecies.objects.filter(is_delete=False).values()
	# context['ranges'] = list(ranges)
	# return JsonResponse(context)
	return render(request,"my_app/tigram/admin/all_species.html",{'ranges':list(ranges),'menu':'species'})

#@group_permissions('add_species')
def add_tree_species(request):
	# context={}
	species_name = request.POST.get('species_name')
	print(request.POST.get('is_noc'),'-----------')
	is_noc = True if request.POST.get('is_noc').lower() == 'true' else False
	ranges = TreeSpecies.objects.create(name=species_name,created_by_id=request.user.id,is_noc=is_noc)
	# messages = "Division added successfully!"
	# context['menu']='forest_officer'
	return JsonResponse({'messages':"Tree Species added successfully!"})

#@group_permissions('edit_species')
def edit_tree_species(request,speci_id):

	species_name = request.POST.get('species_name')
	print(request.POST.get('is_noc'),'-----------')
	is_noc = True if request.POST.get('is_noc') == 'true' else False
	ranges = TreeSpecies.objects.all().values()
	TreeSpecies.objects.filter(id=speci_id).update(name=species_name,is_noc=is_noc)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Species updated successfully!"})

#@group_permissions('delete_division')
def delete_tree_speci(request,speci_id):

	species_name = request.POST.get('species_name')
	TreeSpecies.objects.filter(id=speci_id).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Species deleted successfully!"})

#@group_permissions('delete_divisions')
def delete_tree_species(request):
	delete_list = request.POST.getlist('delete_list[]')
	print(delete_list,'---list')
	# div_name = request.POST.get('div_name')
	TreeSpecies.objects.filter(id__in=delete_list).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Selected Species have been deleted successfully!"})

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('add_range')
def add_range(request):
	# context={}
	range_name = request.POST.get('range_name')
	div_name = request.POST.get('div_name')
	ranges = Range.objects.create(name=range_name,division_id=div_name,created_by=request.user)
	print("Created------")
	return JsonResponse({'messages':"Range added successfully!"})

@group_permissions('edit_range')
def edit_range(request,range_id):
	range_name = request.POST.get('range_name')
	div_name = request.POST.get('div_name')
	# ranges = Range.objects.create(name=range_name,division_id=div_name,created_by=request.user)
	print("Updated------")
	Range.objects.filter(id=range_id).update(name=range_name,division_id=div_name)
	return JsonResponse({'messages':"Range updated successfully!"})

@group_permissions('delete_range')
def delete_range(request,range_id):

	Range.objects.filter(id=range_id).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Range deleted successfully!"})

@group_permissions('delete_ranges')
def delete_ranges(request):
	delete_list = request.POST.getlist('delete_list[]')
	print(delete_list,'---list')
	# div_name = request.POST.get('div_name')
	Range.objects.filter(id__in=delete_list).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Selected Ranges have been deleted successfully!"})

@group_permissions('view_ranges')
def view_ranges(request):
	# context={}
	divisions = Division.objects.all().values()
	ranges = Range.objects.filter(is_delete=False)
	# context['ranges'] = list(ranges)
	# return JsonResponse(context)
	return render(request,"my_app/tigram/admin/all_ranges.html",{'ranges':ranges,'divisions':list(divisions),'menu':'ranges'})


@group_permissions('roles_list')
def roles_list(request):
	# roles_list
	groups_list = Group.objects.filter(is_delete=False).exclude(name='admin').values()
	imp_groups_list = [2,3,4,5,6,7,18]
	return render(request,'my_app/tigram/admin/all_roles.html',{'roles_list':list(groups_list),'imp_groups_list':imp_groups_list,'menu':'roles'})

@group_permissions('add_role')
def add_role(request):
	# context={}
	grp_name = request.POST.get('grp_name')
	print(grp_name)
	if grp_name is not None or grp_name != "":
		grp_name=grp_name.strip()
	count_ = Group.objects.all().count()
	ranges = Group.objects.get_or_create(id=count_+1,name=grp_name)
	print("Created------")
	return JsonResponse({'messages':"Role added successfully!"})

@group_permissions('edit_role')
def edit_role(request,grp_id):
	# context={}
	grp_name = request.POST.get('grp_name')
	if grp_name is not None or grp_name != "":
		grp_name=grp_name.strip()
	ranges = Group.objects.filter(id=grp_id).update(name=grp_name)
	print("Created------")
	return JsonResponse({'messages':"Role updated successfully!"})

@group_permissions('delete_role')
def delete_role(request,role_id):
	imp_groups_list = [2,3,4,5,6,7]
	if role_id not in imp_groups_list:
		Group.objects.filter(id=role_id).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Role deleted successfully!"})

@group_permissions('delete_roles')
def delete_roles(request):
	delete_list = request.POST.getlist('delete_list[]')
	print(delete_list,'---list')
	# div_name = request.POST.get('div_name')
	# imp_groups_list = [2,3,4,5,6,7]
	# if role_id not in imp_groups_list:
	Group.objects.filter(id__in=delete_list).update(is_delete=True)
	# messages = "Division updated successfully!"
	return JsonResponse({'messages':"Selected Roles have been deleted successfully!"})

@login_required
def admin_password(request):
	pass1=request.POST.get('pass1')
	pass2=request.POST.get('pass2')
	if pass1 != pass2:
		return JsonResponse({'messages':"Password doesn't match!"})
	passwd = make_password(pass1)
	CustomUser.objects.filter(id=request.user.id).update(password=passwd)
	return JsonResponse({'messages':'Password Updated Successfully!'})

@login_required
def admin_vpassword(request):
	return render(request,'my_app/tigram/admin/adminchange_password.html',{'menu':'password'})

@login_required
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('summary_report')
def summary_report(request):
	# logo1=settings.SERVER_BASE_URL+settings.DEFAULT_LOGO
	logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
	logo1=settings.SERVER_BASE_URL+settings.USAID_LOGO
	logo2 = settings.SERVER_BASE_URL+settings.KERALAFOREST_LOGO
  #logo3 = settings.SERVER_BASE_URL+"static/images/tigram_logo03.png"
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
		# return message


@login_required
def query(request):
	context={}
	context['groups']=request.user.groups.values_list('name',flat = True)
	return render(request,"my_app/tigram/query.html",context)

def send_msg_otp_signup_verification(phone,name,otp):
    user_id = 0
    # send_status = 'pending'
    # message="not send"
    # name =""
    # phone=""
    # otp=""
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    number = settings.TWILIO_NUMBER
    client = Client(account_sid, auth_token)
    name = name
    phone = phone
    otp =otp
    print("Phone :  "+phone)
    print("Name :  "+name)
    send_status = 'sent'
    message = "sent"
    # otp = "0000"
    # body = "Hi "+str(name)+",Your one time password for Tree Tribe account verification code is "+str(otp)
    # client = Client(account_sid, auth_token)
    # if is_valid_number(phone)==True:
    #     print("***************")
    #     try:
    #         resp = client.messages.create(
    #                                       body=body,
    #                                       from_=number,
    #                                    to=phone)
    #         if resp.status =="queued":
    #             send_status = 'sent'
    #             message = "sent"
    #         elif resp.status =="sent":
    #             send_status = 'sent'
    #             message = "sent"

    #         elif resp.status =="pending":
    #             send_status = 'sent'
    #             message = "sent"
    #         elif resp.status_code =="400":
    #             send_status = 'Not sent'
    #             message = "Not sent"
    #             random_otp =0

    #         else:
    #             send_status = 'Not sent'
    #             message = "Not sent"
    #             random_otp =0
    #     except Exception as ex:
    #         import sys,os
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #         print(exc_type, fname, exc_tb.tb_lineno,"@#@#@#@#")
    #         print(ex,"#####123232")
    #         send_status = 'Error'
    #         message="Not send"

    # else:
    #     print("$$$$$$$$$$$$$$$$$$$$")
    #     message = "Not sent"
    #     random_otp =0


    return message,send_status,otp

def forgot_password_email(email,name,otp):
    subject = 'OTP Verification email from TreeTribe  for Password Change'
    message = ' Hi'+str(name)+' , Please Find Your Otp:'+str(otp)+' For Password Change'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    status = send_mail( subject, message, email_from, recipient_list )
    return status


def forgot_password(request):
	context = {}
	message = ""
	print(request.POST)
	if request.method == 'POST':
		email = request.POST.get('email')

		if email !="":
			email = request.POST.get('email')
			user_exists = CustomUser.objects.filter(email=email)
			print(user_exists,"***********************************90")

			if user_exists:
				otp ="0000"
				# otp = "".join(random.sample("0123456789", 4))
                # status = forgot_password_email(user_exists[0].email,user_exists[0].name,otp)
				print("88888888888888888888")
				otp_chk = SendOtp.objects.filter(otp_owner_id=user_exists[0].id)
				if otp_chk:

					otp1 = SendOtp.objects.filter(otp_owner_id=user_exists[0].id).update(otp=otp,otp_verified=False)
				else:

					otp1 = SendOtp(otp_owner_id=user_exists[0].id,otp=otp)
					otp1.save()

				context["email"] = email
				print(context)
				return render(request,"my_app/tigram/otpverification.html",{"email":email})

				# print(email,"******************")
			else:
				message="Invalid Email"
				print("invalid mail")
				return render(request,"my_app/tigram/forgotpassword.html",{"message":message})

		else:
			phone = request.POST.get('phone')
			print(phone,"*********5656565*********")
			user_exists = CustomUser.objects.filter(phone=phone)
			otp ="0000"
			if user_exists:
				otp_chk = SendOtp.objects.filter(otp_owner_id=user_exists[0].id)
				if otp_chk:
				# otp = "".join(random.sample("0123456789", 4))
					otp ="0000"
					# message,send_status,random_otp=send_msg_otp_signup_verification(user_exists[0].phone,user_exists[0].name,otp)

					otp1 = SendOtp.objects.filter(otp_owner_id=user_exists[0].id).update(otp=otp,otp_verified=False)
				else:
					otp ="0000"
					# otp = "".join(random.sample("0123456789", 4))
					# message,send_status,random_otp=send_msg_otp_signup_verification(user_exists[0].phone,user_exists[0].name,otp)

					otp1 = SendOtp(otp_owner_id=user_exists[0].id,otp=otp)
					otp1.save()


				print(phone,"******************")
				email = phone
				# context["email"] = "email"
				return render(request,"my_app/tigram/otpverification.html",{"email":email})

			else:
				message="Invalid Phone Number"

				print("invalid phone number")
				return render(request,"my_app/tigram/forgotpassword.html",{"message":message})



		# chkemail = CustomUser.objects.filter(email__iexact=email)
		# if chkemail:
		# context["email"] = "email"
		# return render(request,"my_app/tigram/otpverification.html",context)
		# else:
		# 	context["error"] = "Email id not Registered."
		# 	return render(request,"my_app/tigram/forgotpassword.html",context)


	# application_detail = Applicationform.objects.filter(id=app_id).update(reason_range_officer=reason)

	return render(request,"my_app/tigram/forgotpassword.html")


def Otp_verify(request):

	if request.method == 'POST':
		print(request,"*******************((9898")
		email = request.POST.get('email')
		otp = request.POST.get('otp')
		print(otp)
		print(email)

		user_Exist = CustomUser.objects.filter(email=email)
		if user_Exist:
			otp_verify = SendOtp.objects.filter(otp_owner_id=user_Exist[0].id,otp=otp)
			if otp_verify:
				print("899999999999999999989")

				return render(request,"my_app/tigram/newpassword.html",{"email":email})
			else:

				return render(request,"my_app/tigram/otpverification.html",{"temp":"Wrong otp entered.","email":email})
		else:
			return render(request,"my_app/tigram/otpverification.html",{"temp":"Wrong otp entered."})

		# context["email"] = email
		# return render(request,"my_app/tigram/newpassword.html")
	# reason = request.POST.get('reason')
	# application_detail = Applicationform.objects.filter(id=app_id).update(reason_range_officer=reason)

	return render(request,"my_app/tigram/otpverification.html")


def set_newpassword(request):

	if request.method == 'POST':
		# if 'user' in request :
		# user=request.user.id
		print(request)
		passwd = request.POST.get('npass')
		email = request.POST.get('email')

		print(passwd,"****121212**************")
		isuser = CustomUser.objects.filter(email=email)
		if isuser:
		# isuser.set_password(passwd)
			new_password = make_password(passwd)
			isuser.update(password=new_password)
			message = "Password Changed Successfully"
			return render(request,"my_app/tigram/ulogin.html",{'message':message})

		else:
			message="Password not changed"
			print(message)
			return render(request,"my_app/tigram/ulogin.html",{'message':message})
		# email = request.POST.get('email')
		# print(email,"******************")
		# context["email"] = email
		#------ return render(request,"my_app/tigram/ulogin.html")
	# reason = request.POST.get('reason')
	# application_detail = Applicationform.objects.filter(id=app_id).update(reason_range_officer=reason)

	return render(request,"my_app/tigram/newpassword.html")

# def update_password(passwd,uid):
# 		if isuser:
# 		# isuser.set_password(passwd)
# 			new_password = make_password(passwd)
# 			isuser.update(password=new_password)
# 			message = "Password Changed Successfully"
# 			return render(request,"my_app/tigram/ulogin.html",{'message':message})

# 		else:
# 			message="Password not changed"
# 			print(message)
# 	return True

from django.db.models import Count
from .serializers import*
from datetime import timedelta
from django.core import serializers
@login_required(login_url='staff_login')
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('reject_reason')
def reject_reason(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)
	app_list = Applicationform.objects.filter(application_status='R')
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages
	print(app_list)
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		#ajax procedure
		app_list=app_list.values('disapproved_reason')
		len_aplist = len(app_list)
		# dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
  #                                             for reject_type in app_list.annotate(Count('reason_office')) }
		dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist
								 for reject_type in app_list.annotate(Count('disapproved_reason')) }
        # d_dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
        #                                       for reject_type in app_list.annotate(Count('reason_office')) }
		len_aplist = len(app_list)
		# reject_serializer=RejectApplicationSerializer(app_list,many=True)
		# print(type(list(app_list)),'--===---')
		# print(reject_serializer.data)
		# s_data=serializers.serialize('json', app_list)
		# context['app_list'] = list(app_list) #reject_serializer.data#
		context['dict_of_percentages']=dict_of_percentages
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)
		app_list=app_list.values('reason_office','reason_range_officer','reason_depty_ranger_office','disapproved_reason')
		len_aplist = len(app_list)

		dict_of_percentages = { reject_type['disapproved_reason']:reject_type['disapproved_reason__count'] * 100/len_aplist
								 for reject_type in app_list.annotate(Count('disapproved_reason')) }
		context['dict_of_percentages'] =dict_of_percentages
		context['app_list'] = list(app_list)
		early_date = Applicationform.objects.earliest('created_date')
		print(early_date.created_date)
		# d=datetime.strptime(early_date.created_date)
		context['early_date'] = datetime.strftime(early_date.created_date, '%Y-%m-%d')
		# context['early_date'] =d.strftime('%Y-%m-%d')
		# context['early_date'] =
		context['today'] = datetime.strftime(datetime.today(),'%Y-%m-%d')
		context['to_date']=to_date
		context['from_date']=from_date
		context['select_mon']=select_mon
	return render(request,'my_app/tigram/app_rejection.html',context)

from django.db.models import Count, Case,Sum, When, CharField,IntegerField,DecimalField,FloatField, F
@login_required(login_url='staff_login')
# @group_required('revenue officer','deputy range officer','forest range officer')
@group_permissions('no_of_applicantions')
def no_of_applicantions(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)
	# app_list = Applicationform.objects.values(
 #    'created_date'
	# ).annotate(
	#     no_of_received=Count('pk')
	# ).annotate(
	#     no_of_approved=Count(Case(
	#     	When(application_status='A',then=F('id')),
	#     	output_field=IntegerField(),))
	# ).annotate(
	#     no_of_rejected=Count(Case(
	#     	When(application_status='R',then=F('id')),
	#     	output_field=IntegerField(),))
	# ).order_by('created_date')
	print(request,'---')
	range_name = request.GET.get('range_name',None)
	village_type = request.GET.get('village_type',None)
	app_list = Applicationform.objects.filter(is_noc=False)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(area_range__icontains=range_name[0].range_name.name)		
	else:
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(division__icontains=div_name[0].division_name.name)
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages            
	print(app_list)                             
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(is_form_two=village_type)
		total_approved_applicant=app_list.filter(application_status='A').count()
		total_rejected_applicant=app_list.filter(application_status='R').count()
		app_list=app_list.values(
		'created_date'
		).annotate(
		no_of_received=Count('pk')
		).annotate(
		no_of_approved=Count(Case(
			When(application_status='A',then=F('id')),
			output_field=IntegerField(),))
		).annotate(
		no_of_rejected=Count(Case(
			When(application_status='R',then=F('id')),
			output_field=IntegerField(),))
		).order_by('created_date')
		#ajax procedure
		# app_list=app_list.values('reason_office')
		len_aplist = len(app_list)
		# dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
  #                                             for reject_type in app_list.annotate(Count('reason_office')) }
        # d_dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
        #                                       for reject_type in app_list.annotate(Count('reason_office')) }
		# reject_serializer=RejectApplicationSerializer(app_list,many=True)
		# print(type(list(app_list)),'--===---')
		# print(reject_serializer.data)
		# s_data=serializers.serialize('json', app_list)
		# context['app_list'] = list(app_list) #reject_serializer.data#
		context['applicantions']=list(app_list)
		context['total_rejected_applicant']=total_rejected_applicant
		context['total_approved_applicant']=total_approved_applicant
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)
		app_list=app_list.values('reason_office','reason_range_officer','reason_depty_ranger_office')
		len_aplist = len(app_list)

		dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
								 for reject_type in app_list.annotate(Count('reason_office')) }
		context['dict_of_percentages'] =dict_of_percentages
		context['app_list'] = list(app_list)
		early_date = Applicationform.objects.earliest('created_date')
		print(early_date.created_date)
		# d=datetime.strptime(early_date.created_date)
		context['early_date'] = datetime.strftime(early_date.created_date, '%Y-%m-%d')
		# context['early_date'] =d.strftime('%Y-%m-%d')
		# context['early_date'] =
		context['today'] = datetime.strftime(datetime.today(),'%Y-%m-%d')
		context['to_date']=to_date
		context['from_date']=from_date
		context['select_mon']=select_mon
	return render(request,'my_app/tigram/tabel_01.html',context)

from django.db.models.functions import Cast
@group_permissions('species_wise_transport')
def species_wise_transport(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)
	sel_sp = request.GET.get('sel_sp')

	app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	applications_list=Applicationform.objects.filter(is_noc=False)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(appform__area_range__icontains=range_name[0].range_name.name)
		applications_list=applications_list.filter(area_range__icontains=range_name[0].range_name.name)
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
		# 	applications_list=applications_list.filter(division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(appform__area_range__icontains=range_name)
		# 	applications_list=applications_list.filter(area_range__icontains=range_name)
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(appform__area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(appform__division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
	print(app_list)
# .aggregate(Sum('volume'))
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(appform__created_date__gte=six_month_previous_date)
			applications_list= applications_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(appform__created_date__gte=date_)
				applications_list= applications_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(appform__created_date__lte=date_)
				applications_list= applications_list.filter(created_date__lte=date_)
		if sel_sp != '' and sel_sp != None:
			print(sel_sp,'----selected species------')
			app_list=app_list.filter(species_of_tree__icontains=sel_sp)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(appform__is_form_two=village_type)
		#ajax procedure
		# app_list=app_list.values('reason_office')
		app_list=app_list.values('species_of_tree',
		'appform__created_date').annotate(
		 no_of_trees=Count('species_of_tree')
		).annotate(
		 total_no_of_trees=Count('id')
		).annotate(
		volume_sum=Sum('volume')
		)
		len_aplist = len(app_list)
		applications_list = applications_list.values('created_date').order_by('-created_date').annotate(
			as_float=Cast('total_trees', IntegerField())
			).annotate(
			total_trees=Sum('as_float'),
			)
		# dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
  #                                             for reject_type in app_list.annotate(Count('reason_office')) }
        # d_dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
        #                                       for reject_type in app_list.annotate(Count('reason_office')) }
		# reject_serializer=RejectApplicationSerializer(app_list,many=True)
		# print(type(list(app_list)),'--===---')
		# print(reject_serializer.data)
		# s_data=serializers.serialize('json', app_list)
		# context['app_list'] = list(app_list) #reject_serializer.data#
		context['applicantions']=list(app_list)
		context['applications_list']=list(applications_list)
		#context['applicantions']=list(app_list)
		trees_species_list = TreeSpecies.objects.filter(is_noc=False).values('name')
		context['trees_species'] = list(trees_species_list)
		context['trees_species_length']=len(context['trees_species'])
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

		# context['early_date'] = datetime.strftime(early_date.created_date, '%Y-%m-%d')
		# # context['early_date'] =d.strftime('%Y-%m-%d')
		# # context['early_date'] =
		# context['today'] = datetime.strftime(datetime.today(),'%Y-%m-%d')
		# context['to_date']=to_date
		# context['from_date']=from_date
		# context['select_mon']=select_mon
	return render(request,'my_app/tigram/tabel_01.html',context)

@group_permissions('species_wise_dest_transport')
def species_wise_dest_transport(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)
	sel_sp = request.GET.get('sel_sp')

	app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	#applications_list=Applicationform.objects.filter(is_noc=False)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(appform__area_range__icontains=range_name[0].range_name.name)
		#applications_list=applications_list.filter(area_range__icontains=range_name[0].range_name.name)		
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
		# 	applications_list=applications_list.filter(division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(appform__area_range__icontains=range_name)
		# 	applications_list=applications_list.filter(area_range__icontains=range_name)

		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(appform__area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(appform__division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)

		#applications_list=applications_list.filter(division__icontains=div_name[0].division_name.name)
	print(app_list)                             
# .aggregate(Sum('volume'))
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages            
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(appform__created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(appform__created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(appform__created_date__lte=date_)
		if sel_sp != '' and sel_sp != None:
			print(sel_sp,'----selected species------')
			app_list=app_list.filter(species_of_tree__icontains=sel_sp)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(appform__is_form_two=village_type)
		#ajax procedure
		# app_list=app_list.values('reason_office')
		app_list=app_list.values('species_of_tree','appform__destination_details',
		'appform__created_date').annotate(
		 no_of_trees=Count('species_of_tree')	
		).annotate(
		volume_sum=Sum('volume')
		).order_by('appform__created_date')
		len_aplist = len(app_list)

		context['applicantions']=list(app_list)
		#context['applicantions']=list(app_list)
		trees_species_list = TreeSpecies.objects.filter(is_noc=False).values('name')
		context['trees_species'] = list(trees_species_list)
		context['trees_species_length']=len(context['trees_species'])
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

	return render(request,'my_app/tigram/tabel_01.html',context)

@group_permissions('trees_transport')
def trees_transport(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(appform__area_range__icontains=range_name[0].range_name.name)
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(appform__area_range__icontains=range_name)
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(appform__area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(appform__division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
# .aggregate(Sum('volume'))
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages            
	print(app_list)                             
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(appform__created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(appform__created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(appform__created_date__lte=date_)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(appform__is_form_two=village_type)
		#ajax procedure
		# app_list=app_list.values('reason_office')
		app_list=app_list.values(
		'appform__created_date').annotate(
		 no_of_trees=Count('species_of_tree')	
		).annotate(
		volume_sum=Sum('volume')
		)
		len_aplist = len(app_list)
		# dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
  #                                             for reject_type in app_list.annotate(Count('reason_office')) }
        # d_dict_of_percentages = { reject_type['reason_office']:reject_type['reason_office__count'] * 100/len_aplist
        #                                       for reject_type in app_list.annotate(Count('reason_office')) }
		# reject_serializer=RejectApplicationSerializer(app_list,many=True)
		# print(type(list(app_list)),'--===---')
		# print(reject_serializer.data)
		# s_data=serializers.serialize('json', app_list)
		# context['app_list'] = list(app_list) #reject_serializer.data#
		context['applicantions']=list(app_list)
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

		# context['early_date'] = datetime.strftime(early_date.created_date, '%Y-%m-%d')
		# # context['early_date'] =d.strftime('%Y-%m-%d')
		# # context['early_date'] =
		# context['today'] = datetime.strftime(datetime.today(),'%Y-%m-%d')
		# context['to_date']=to_date
		# context['from_date']=from_date
		# context['select_mon']=select_mon
	return render(request,'my_app/tigram/tabel_01.html',context)

@group_permissions('total_volume_dest')
def total_volume_dest(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(appform__area_range__icontains=range_name[0].range_name.name)
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(appform__area_range__icontains=range_name)
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(appform__area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(appform__division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
# .aggregate(Sum('volume'))
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages            
	print(app_list)                             
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(appform__created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(appform__created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(appform__created_date__lte=date_)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(appform__is_form_two=village_type)
		#ajax procedure
		# app_list=app_list.values('reason_office')
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
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

	return render(request,'my_app/tigram/tabel_01.html',context)
from django.db.models.functions import ExtractDay

@group_permissions('approval_time_report')
def approval_time_report(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	app_list = Applicationform.objects.filter(application_status='A',is_noc=False)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(area_range__icontains=range_name[0].range_name.name)
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(area_range__icontains=range_name)
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(division__icontains=div_name[0].division_name.name)
# .aggregate(Sum('volume'))
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages            
	print(app_list)
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(is_form_two=village_type)
		#ajax procedure
		# app_list=app_list.values('reason_office')
		# app_list=app_list.filter(application_status='A')
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
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

	return render(request,'my_app/tigram/tabel_01.html',context)

@group_permissions('cutting_reasons_report')
def cutting_reasons_report(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	app_list = Applicationform.objects.filter(is_noc=False)
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(area_range__icontains=range_name[0].range_name.name)
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(area_range__icontains=range_name)
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(division__icontains=div_name[0].division_name.name)

	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(is_form_two=village_type)
		#ajax procedure
		# app_list=app_list.values('reason_office')
		# app_list=app_list.filter(application_status='A')
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
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

	return render(request,'my_app/tigram/tabel_01.html',context)

@group_permissions('trees_cutted_report')
def trees_cutted_report(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	app_list = Timberlogdetails.objects.filter(appform__is_noc=False)
	sel_sp = request.GET.get('sel_sp')
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(appform__area_range__icontains=range_name[0].range_name.name)
	else:
		# if range_name=="" or range_name == None :
		# 	div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
		# 	app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
		# else:
		# 	app_list = app_list.filter(appform__area_range__icontains=range_name)
		div_name1 = request.GET.get('div_name',None)
		div_name=""
		if range_name=="" or range_name == None :
			pass
		else:	
			app_list = app_list.filter(appform__area_range__icontains=range_name)
		# if groups[0] not in ['state officer']:
		if groups[0] in ['state officer']:
				print(div_name1,'----div')
				if div_name1=="" or div_name1 == None :
					# div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
					pass
				else:
					app_list = app_list.filter(appform__division__iexact=div_name1)
		else:
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
	print(app_list)                             
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')                                   
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(appform__created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(appform__created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(appform__created_date__lte=date_)
		if sel_sp != '' and sel_sp != None:
			print(sel_sp,'----selected species------')
			app_list=app_list.filter(species_of_tree__icontains=sel_sp)
		village_type = request.GET.get('village_type',None)
		if village_type =="both"or village_type==None :
			pass
		else:
			app_list=app_list.filter(appform__is_form_two=village_type)
		# else:

		#ajax procedure
		# app_list=app_list.values('reason_office')
		# app_list=app_list.filter(application_status='A')
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
		# trees=load_tree_species()

		trees_species_list = TreeSpecies.objects.filter(is_noc=False).values('name')
		context['trees_species'] = list(trees_species_list)
		context['trees_species_length']=len(context['trees_species'])
		context['len_aplist']=len_aplist
		print(trees_species_list)
		# context['trees']=list(trees)
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

		return render(request,'my_app/tigram/tabel_01.html',context)

# @group_permissions('noc_report')
def noc_report2(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	app_list = Applicationform.objects.filter(is_noc=True)
	sel_sp = request.GET.get('sel_sp')
		# .aggregate(Sum('volume'))
	# created_date__gte=six_month_previous_date,
	# app_list['dict_of_percentages']=dict_of_percentages
	print(app_list)
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# if sel_sp != '' and sel_sp != None:
		# 	print(sel_sp,'----selected species------')
		# 	app_list=app_list.filter(species_of_tree__icontains=sel_sp)
		# else:

		#ajax procedure
		# app_list=app_list.values('reason_office')
		# app_list=app_list.filter(application_status='A')
		totalapp=app_list.count()
		print(totalapp,'-----xxxxxxxxx---------')
		app_list=app_list.values(
		'created_date').annotate(
		no_of_applicantions=Count('id')
		).order_by('created_date')
		len_aplist = len(app_list)

		context['applicantions']=list(app_list)
		# trees=load_tree_species()

		trees_species_list = TreeSpecies.objects.filter(is_noc=True).values('name')
		context['trees_species'] = list(trees_species_list)
		context['trees_species_length']=len(context['trees_species'])
		context['len_aplist']=len_aplist
		print(trees_species_list)
		# context['trees']=list(trees)
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)

	return render(request,'my_app/tigram/tabel_01.html',context)

def noc_report(request):
	context={}
	groups=request.user.groups.values_list('name',flat = True)
	select_mon = request.GET.get('select_mon',None)
	# context['group'] = groups
	current_date = date.today()
	print(select_mon,'=======')
	from_date = request.GET.get('from_date',None)
	to_date = request.GET.get('to_date',None)

	app_list = Timberlogdetails.objects.filter(appform__is_noc=True)
	sel_sp = request.GET.get('sel_sp')
	range_name = request.GET.get('range_name',None)
	div_name = request.GET.get('div_name',None)
	if request.user.groups.filter(name__in=['revenue officer','deputy range officer','forest range officer']).exists():
		if groups[0] in ['revenue officer']:
			range_name = RevenueOfficerdetail.objects.filter(Rev_user_id=request.user.id)
		else:
			range_name = ForestOfficerdetail.objects.filter(fod_user_id=request.user.id)
		app_list = app_list.filter(appform__area_range__icontains=range_name[0].range_name.name)
	else:
		if range_name=="" or range_name == None :
			div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id)
			app_list = app_list.filter(appform__division__icontains=div_name[0].division_name.name)
		else:
			app_list = app_list.filter(appform__area_range__icontains=range_name)
	print(app_list)
	# context['dict_of_percentages'] =dict_of_percentages
	# print(dict_of_percentages,'---------')
	# context['app_list'] = app_list
	if request.is_ajax():
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(appform__created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(appform__created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(appform__created_date__lte=date_)
		if sel_sp != '' and sel_sp != None:
			print(sel_sp,'----selected species------')
			app_list=app_list.filter(species_of_tree__icontains=sel_sp)
		#ajax procedure
		# app_list=app_list.values('reason_office')
		app_list=app_list.values('species_of_tree','appform__destination_details',
		'appform__created_date').annotate(
		 no_of_trees=Count('species_of_tree')
		).annotate(
		volume_sum=Sum('volume')
		).order_by('appform__created_date')
		len_aplist = len(app_list)

		context['applicantions']=list(app_list)
		trees_species_list = TreeSpecies.objects.filter(is_noc=True).values('name')
		context['trees_species'] = list(trees_species_list)
		context['trees_species_length']=len(context['trees_species'])
		# context['group'] = list(groups)
		print(context,'--=context')
		return JsonResponse(context,safe=False)
	else:
		if (select_mon is  None or select_mon =='') and (from_date is  None or from_date=='') and (to_date is  None or to_date=='' ):
			select_mon = 6
		if  select_mon !='' and select_mon !=  None :

			months_ago = float(select_mon)
			# months_ago = float(select_mon) if select_mon is not None else 3 #12
			six_month_previous_date = current_date - timedelta(days=(months_ago * 365 / 12))
			print(six_month_previous_date)
			app_list=app_list.filter(created_date__gte=six_month_previous_date)
		else:
			print(to_date,'---==',from_date,'++++')

			if from_date !='' and from_date != None and from_date != 'None'  :
				print('im in from',type(from_date))

				date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(from_date,'%Y-%m-%d')
				# from_date=d.strftime(from_date)
				app_list=app_list.filter(created_date__gte=date_)
			if to_date !='' and to_date != None and to_date != 'None':
				print('im in to',type(to_date))
				date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%Y-%m-%d')
				# d=datetime.strptime(to_date,'%Y-%m-%d')
				# to_date=d.strftime(to_date)
				app_list=app_list.filter(created_date__lte=date_)
		# print(date_,'====---')
		print(app_list)

		len_aplist = len(app_list)
	return render(request,'my_app/tigram/tabel_01.html',context)


@login_required(login_url='staff_login')
@group_required('revenue officer','deputy range officer','forest range officer','division officer','state officer')
def all_reports(request):
	context={}
	context['area_range_name']=request.GET.get('range_name',None)
	context['area_div_name']=request.GET.get('div_name',None)
	context['groups']=request.user.groups.values_list('name',flat = True)
	context['current_page']='report_section'
	print(context['groups'][0],'-----A')
	if context['groups'][0] == 'division officer':
		context['area_range_name']= "" if context['area_range_name'] == "" or context['area_range_name']==None else context['area_range_name']
		div_name = DivisionOfficerdetail.objects.filter(div_user_id=request.user.id).values_list('division_name',flat=True)
		context['area_range'] =Range.objects.filter(division_id=div_name[0]).values_list('name',flat=True)
	if context['groups'][0] == 'state officer':
		context['area_div_name']= "" if context['area_div_name'] == "" or context['area_div_name']==None else context['area_div_name']
		context['area_range_name']= "" if context['area_range_name'] == "" or context['area_range_name']==None else context['area_range_name']
		context['division_name'] = Division.objects.filter(is_delete=False).values_list('name',flat=True)
		# context['area_range'] =Range.objects.filter(division_id=div_name[0]).values_list('name',flat=True)
		div_id=context['area_div_name']
		if div_id.isdigit():
			context['area_range'] = Range.objects.filter(division_id=div_id,is_delete=False).values_list('name',flat=True)
		else:
			context['area_range'] = Range.objects.filter(division__name__iexact=div_id,is_delete=False).values_list('name',flat=True)
			print(context['area_range'],'-----')	
		if len(context['area_range'])<1 and div_id=="" or div_id==None:
			context['area_range'] = Range.objects.filter(is_delete=False).values_list('name',flat=True)
		# context['area_range'] = Range.objects.filter(division__icontains=div_name)
	return render(request,'my_app/tigram/reports_tables_02.html',context)

# @login_required
# @group_required('revenue officer','deputy range officer','forest range officer','user')
# @group_permissions('scanqr')
def scanqr(request,code):
	url = code.rsplit('/', 1)[-1]
	print(request.user.id)
	tp = TransitPass.objects.filter(qr_code=url)
	if request.user.id is not None:

		groups=request.user.groups.values_list('name',flat = True)
		# print(groups,'----group')
		user_id = request.user.id
		if tp:
			if groups[0]=='user' and tp[0].app_form.by_user_id!=user_id:
				return HttpResponseNotFound('<h1>Page Not Found! </h1>')
			return HttpResponseRedirect(reverse('transit_pass_pdf', kwargs={'applicant_no':tp[0].app_form_id}))
			# return render(request,"my_app/tigram/newpassword.html",{})
		else:
			return HttpResponseNotFound('<h1>Page Not Found! </h1>')
	else:
		context={}
		if tp:
			application = Applicationform.objects.filter(id=tp[0].app_form_id)
			print(application)
			if application:
				authorizer_name = application[0].approved_by.name
				context['authorizer_name'] = authorizer_name
				application=application.values()
				context['applications']=application
			log_details = Timberlogdetails.objects.filter(appform_id=tp[0].app_form_id).values()
			context['tp']=tp[0]
			# Applicationform
			context['log_details']=log_details
		return render(request,'my_app/tigram/transit_pass_scan.html',context)
		# return HttpResponseNotFound('<h1>Page Not Found! </h1>')
	return HttpResponseNotFound('<h1>Page Not Found! </h1>')

# @login_required
# # @group_required('revenue officer','deputy range officer','forest range officer','user')
# @group_permissions('scanqr')
# def scanqr(request,code):
# 	url = code.rsplit('/', 1)[-1]
# 	groups=request.user.groups.values_list('name',flat = True)
# 	# print(groups,'----group')
# 	tp = TransitPass.objects.filter(qr_code=url)
# 	user_id = request.user.id
# 	if tp:
# 		if groups[0]=='user' and tp[0].app_form.by_user_id!=user_id:
# 			return HttpResponseNotFound('<h1>Page Not Found! </h1>')
# 		return HttpResponseRedirect(reverse('transit_pass_pdf', kwargs={'applicant_no':tp[0].app_form_id}))
# 		# return render(request,"my_app/tigram/newpassword.html",{})
# 	else:
# 		return HttpResponseNotFound('<h1>Page Not Found! </h1>')
# 	return HttpResponseNotFound('<h1>Page Not Found! </h1>')


@login_required
# @group_required('revenue officer','deputy range officer','forest range officer','user')
@group_permissions('scan_logqr')
def scan_logqr(request,code):
	url = code.rsplit('/', 1)[-1]
	groups=request.user.groups.values_list('name',flat = True)
	# print(groups,'----group')
	tp = Timberlogdetails.objects.filter(log_qr_code=url)
	user_id = request.user.id
	if tp:
		if groups[0]=='user' and tp[0].app_form.by_user_id!=user_id:
			return HttpResponseNotFound('<h1>Page Not Found! </h1>')
		# return redirect()
		return HttpResponseRedirect(reverse('log_qrcode_pdf', kwargs={'log_no':tp[0].id}))
		# return render(request,"my_app/tigram/newpassword.html",{})
	else:
		return HttpResponseNotFound('<h1>Page Not Found! </h1>')
	return HttpResponseNotFound('<h1>Page Not Found! </h1>')



def view_reasons(request):
	applicants =  Applicationform.objects.filter(created_date='27/7/2020')
	return JsonResponse({'applicants':applicants})


def test_sample():
	# print(datetime.datetime.today()-datetime.timedelta(days=30))
	# temp=Applicationform.objects.filter(transit_pass_created_date__gt=datetime.datetime.today()-datetime.timedelta(days=20)).update(
	# 	tp_expiry_date=datetime.datetime.today(),tp_expiry_status=True
	# 	)
	temp=Applicationform.objects.filter(transit_pass_created_date__gt=date.today()-timedelta(days=20)).update(
		tp_expiry_date=date.today(),tp_expiry_status=True
		)
	#
	print("From Schedular*********************")


def approve_deemed():
	print(date.today()-timedelta(days=7),'---day')
	#
	app_id_list=Applicationform.objects.filter(
	verify_office = True,is_noc=False,
	deemed_approval=False,
	# transit_pass_id__isnull=True,
	verify_office_date__lt=date.today()-timedelta(days=7)).exclude(Q(application_status='A')|Q(application_status='R')).values_list('id',flat=True)
	print(app_id_list)
	if len(app_id_list)<1:

		print('not approved')
		return True
	for app_id in app_id_list:
				application_detail = Applicationform.objects.filter(id=app_id)
				vehicle_detail = Vehicle_detials.objects.filter(app_form_id=app_id)
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
					# reason_range_officer = reason ,
				 application_status = 'A',
					# approved_by = request.user,
					# verify_range_officer = True,
					# range_officer_date = date.today(),
					transit_pass_id=transit_pass.id,
					transit_pass_created_date = date.today(),
					)
	temp=Applicationform.objects.filter(
	verify_office = True,is_noc=False,
	# deemed_approval=False,
	verify_office_date__lt=date.today()-timedelta(days=7)).update(
	deemed_approval=True,transit_pass_created_date=date.today()
	)
	print(temp,'')
	print("From Deemed Schedular *********************")

def approve_deemed_form_two_1():
	print(date.today()-timedelta(days=7),'---day')
	#
	app_id_list=Applicationform.objects.filter(
	verify_office = True,is_noc=False,log_updated_by_user=False,
	deemed_approval=False,is_form_two=True,
	verify_office_date__lt=date.today()-timedelta(days=7)).exclude(Q(application_status='A')|Q(application_status='R')).update(
		deputy2_date=date.today(),
		verify_deputy2=True,
		deemed_approval_1=True,
	)
	# print(app_id_list)
	
	print("Form 2 Stage 1 Deemed Schedular *********************")

def approve_deemed_form_two():
	print(date.today()-timedelta(days=7),'---day')
	#
	app_id_list=Applicationform.objects.filter(
	verify_office = True,is_noc=False,log_updated_by_user=True,
	deemed_approval=False,is_form_two=True,
	appsecond_two_date__lt=date.today()-timedelta(days=7)).exclude(Q(application_status='A')|Q(application_status='R')).values_list('id',flat=True)
	# print(app_id_list)
	if len(app_id_list)<1:
		print('not approved')
		return True
	for app_id in app_id_list:
				application_detail = Applicationform.objects.filter(id=app_id)
				vehicle_detail = Vehicle_detials.objects.filter(app_form_id=app_id)
				qr_code=get_qr_code(app_id)
				# print(qr_code,'-----QR')
				qr_img=generate_qrcode_image(qr_code, settings.QRCODE_PATH, app_id)
				# print(qr_img,'----qr_path')
				is_timber = Timberlogdetails.objects.filter(appform_id=app_id)
				if is_timber:
					for each_timber in is_timber.values('id','species_of_tree','latitude','longitude','length','breadth','volume'):
						log_qr_code=get_log_qr_code(app_id,each_timber['id'])
						# print(log_qr_code,'-----LOG QR')
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
						# print(log_qr_img,'----qr_path')
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
					# reason_range_officer = reason ,
				 application_status = 'A',
					# approved_by = request.user,
					# verify_range_officer = True,
					# range_officer_date = date.today(),
					deemed_approval=True,
					transit_pass_id=transit_pass.id,
					transit_pass_created_date = date.today(),
					) 
	# temp=Applicationform.objects.filter(
	# verify_office = True,is_noc=False,is_form_two=True,
	# # deemed_approval=False,
	# verify_office_date__lt=date.today()-timedelta(days=7)).update(
	# deemed_approval=True,transit_pass_created_date=date.today()	
	# )
	print(temp,'')
	print("Form 2 Stage 2 Deemed Schedular *********************")