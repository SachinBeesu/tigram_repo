from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from .managers import CustomUserManager
from datetime import datetime, date
from django.conf import settings
from django.contrib.auth.models import Group

Group.add_to_class('is_delete', models.BooleanField(default=False))
# Create your models here.
STATUS_CHOICES = (
    ('S', _("Submitted")),
    ('P', _("Pending")),
    ('A', _("Approved")),
    ('R', _("Rejected")),
)

class CustomUser(AbstractUser):

    username = None
    user_id = models.CharField(max_length=30,blank=True,null=True)
    phone = models.CharField(max_length=20,unique=True)
    name = models.CharField(max_length=50,blank=True,null=True)
    email = models.CharField(max_length=50,blank=True,null=True,unique=True)
    signup_date = models.DateTimeField(auto_now_add=True)
    login_date = models.DateTimeField(auto_now_add=True)
    login_status = models.CharField(max_length=255, default='')
    profile_pic = models.CharField(max_length=255, default='')
    user_status = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=255, default='')
    photo_proof_img = models.CharField(max_length=255,default='no_image.png')
    photo_proof_no = models.CharField(max_length=255,blank=True,null=True)
    photo_proof_name = models.CharField(max_length=255,blank=True,null=True)
    photo_proof_type = models.ForeignKey('PhotoProof', on_delete=models.CASCADE,blank=True,null=True,related_name = 'custom_user_photo_proof')
    aadhar_detail = models.CharField(max_length=25, default='')
    is_delete=models.BooleanField(default=False)
    # ngo_allocated = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def __unicode__(self):
        return self.id

class PhotoProof(models.Model):
    name = models.CharField(max_length=200,blank=True,null=True)
    is_delete = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'photo_proof_user')
    def __unicode__(self):
        return self.id

class TreeSpecies(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    is_delete = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'tree_species_user')
    is_noc = models.BooleanField(default=False)
    def __unicode__(self):
        return self.id

class State(models.Model):
    name=models.CharField(max_length=225,blank=True,null=True)
    created_date =models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'state_created_by')
    is_delete =models.BooleanField(default=False)
    
class Division(models.Model):
    name=models.CharField(max_length=225,blank=True,null=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE,blank=True,null=True,related_name = 'division_state')
    created_date =models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'division_created_by')
    is_delete =models.BooleanField(default=False)

class Range(models.Model):
    name=models.CharField(max_length=225,blank=True,null=True)
    created_date =models.DateField(auto_now_add=True)
    division = models.ForeignKey(Division,on_delete=models.CASCADE,blank=True,null=True,related_name = 'range_division')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'range_created_by')
    is_delete =models.BooleanField(default=False)

class DivisionOfficerdetail(models.Model):
    div_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'dod_div_user')
    post = models.CharField(max_length=200,blank=True,null=True)
    office_address = models.CharField(max_length=500,blank=True,null=True)
    division_name = models.ForeignKey(Division, on_delete=models.CASCADE,blank=True,null=True,related_name = 'dod_div')

class StateOfficerdetail(models.Model):
    state_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'sod_state_user')
    post = models.CharField(max_length=200,blank=True,null=True)
    office_address = models.CharField(max_length=500,blank=True,null=True)
    state_name = models.CharField(max_length=200,blank=True,null=True)

class ForestOfficerdetail(models.Model):
    fod_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'fod_user')
    post = models.CharField(max_length=200,blank=True,null=True)
    office_address = models.CharField(max_length=500,blank=True,null=True)
    range_name = models.ForeignKey(Range, on_delete=models.CASCADE,blank=True,null=True,related_name = 'fod_range')
    division_name = models.ForeignKey(Division, on_delete=models.CASCADE,blank=True,null=True,related_name = 'fod_div')



class RevenueOfficerdetail(models.Model):
    Rev_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'rev_user')
    post = models.CharField(max_length=200,blank=True,null=True)
    office_address = models.CharField(max_length=500,blank=True,null=True)
    range_name = models.ForeignKey(Range, on_delete=models.CASCADE,blank=True,null=True,related_name = 'rev_range')
    division_name = models.ForeignKey(Division, on_delete=models.CASCADE,blank=True,null=True,related_name = 'rev_div')

class SendOtp(models.Model):
    otp_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='user', related_query_name='user')
    otp = models.CharField(max_length=20,blank=True,null=True)
    otp_verified = models.BooleanField(default=False)
    def _unicode_(self):
        return self.id

class Applicationform(models.Model):
    application_no = models.CharField(max_length=100,blank=True,null=True) 
    by_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_by_user')
    name = models.CharField(max_length=100,blank=True,null=True)
    address = models.CharField(max_length=500,blank=True,null=True)
    survey_no = models.CharField(max_length=50,blank=True,null=True)    
    state = models.CharField(max_length=255,blank=True,default='')
    other_state = models.BooleanField(default=False)
    district = models.CharField(max_length=255,blank=True)
    taluka = models.CharField(max_length=255,blank=True)
    block = models.CharField(max_length=255,default='')
    division = models.CharField(max_length=255,blank=True)
    area_range = models.CharField(max_length=255,blank=True)
    pincode = models.CharField(max_length=15,blank=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_approved_by')
    proof_of_ownership_of_tree = models.CharField(max_length=255,blank=True)
    village = models.CharField(max_length=255,default='')
    species_of_trees = models.CharField(max_length=255,default='')
    purpose = models.CharField(max_length=255,default='')
    trees_proposed_to_cut = models.CharField(max_length=255,default='')
    trees_cutted = models.BooleanField(default=False)
    total_trees = models.CharField(max_length=255,default='')
    destination_details = models.CharField(max_length=500,default='')
    destination_state = models.CharField(max_length=500,default='')
    signature_img = models.BooleanField(default=False)
    revenue_application = models.BooleanField(default=False)
    location_sktech = models.BooleanField(default=False)
    tree_ownership_detail = models.BooleanField(default=False)
    aadhar_detail = models.BooleanField(default=False)
    application_status = models.CharField(choices=STATUS_CHOICES, default='S',max_length=3)
    disapproved_reason = models.CharField(max_length=500,default='')
    verify_office = models.BooleanField(default=False)
    reason_office = models.CharField(max_length=500,default='')
    verify_office_date = models.DateField(blank=True,null=True)
    depty_range_officer = models.BooleanField(default=False)
    reason_depty_ranger_office = models.CharField(max_length=500,default='')
    deputy_officer_date = models.DateField(blank=True,null=True)
    verify_range_officer = models.BooleanField(default=False)
    reason_range_officer = models.CharField(max_length=500,default='')
    range_officer_date = models.DateField(blank=True,null=True)
    division_officer = models.BooleanField(default=False)
    reason_division_officer = models.CharField(max_length=500,default='')
    division_officer_date = models.DateField(blank=True,null=True)
    payment = models.CharField(max_length=100,default='')
    created_date = models.DateField(auto_now_add=True)
    appsecond_one_date = models.DateField(blank=True,null=True)
    appsecond_two_date = models.DateField(blank=True,null=True)
    deputy2_date = models.DateField(blank=True,null=True)
    transit_pass_created_date = models.DateField(default='2021-03-19',blank=True,null=True)
    transit_pass_id = models.IntegerField(default=0)
    tp_expiry_status=models.BooleanField(default=False)
    tp_expiry_date = models.DateField(default='2021-03-19')
    verify_deputy2 = models.BooleanField(default=False)
    reason_deputy2 = models.CharField(max_length=500,default='')
    deputy2_date = models.DateField(blank=True,null=True)
    approved_by_deputy2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_approved_by_deputy2')
    approved_by_deputy = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_approved_by_deputy')
    approved_by_revenue = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_approved_by_revenue')
    approved_by_division = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_approved_by_division')
    disapproved_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'applicationform_disapproved_by')
    disapproved_by_grp = models.CharField(max_length=50,default='')
    log_updated_by_user = models.BooleanField(default=False)
    is_noc = models.BooleanField(default=False)
    is_form_two = models.BooleanField(default=False)
    deemed_approval = models.BooleanField(default=False)
    deemed_approval_1 = models.BooleanField(default=False)
    def __unicode__(self):
        return self.id

class Timberlogdetails(models.Model):
    appform= models.ForeignKey(Applicationform, on_delete=models.CASCADE,blank=True,null=True,related_name = 'app_id')

    species_of_tree = models.CharField(max_length=100,blank=True,null=True)
    length = models.FloatField(blank=True,null=True)
    breadth = models.FloatField(blank=True,null=True)

    volume = models.FloatField(blank=True,null=True)
    latitude = models.FloatField(blank=True,null=True)
    longitude = models.FloatField(blank=True,null=True)
    log_qr_code = models.CharField(max_length=200,blank=True,null=True)
    log_qr_code_img = models.CharField(max_length=200,blank=True,null=True)

    
    def __unicode__(self):
        return self.id

class Species_geodetails(models.Model):
    appform= models.ForeignKey(Applicationform, on_delete=models.CASCADE,blank=True,null=True,related_name = 'species_detaila_app_id')
    species_tree = models.ForeignKey(TreeSpecies,on_delete=models.CASCADE,blank=True,null=True,related_name = 'species_geodetails_species_name')
    latitude = models.FloatField(blank=True,null=True)
    longitude = models.FloatField(blank=True,null=True)
    def __unicode__(self):
        return self.id


class Vehicle_detials(models.Model):
    app_form= models.ForeignKey(Applicationform, on_delete=models.CASCADE,blank=True,null=True,related_name = 'app_vehicle')

    vehicle_reg_no = models.CharField(max_length=100,blank=True,null=True)
    driver_name = models.CharField(max_length=200,blank=True,null=True)
    driver_phone = models.CharField(max_length=20,blank=True,null=True)
    mode_of_transport = models.CharField(max_length=200,blank=True,null=True)
    license_image = models.CharField(max_length=200,blank=True,null=True)
    photo_of_vehicle_with_number = models.CharField(max_length=200,blank=True,null=True)

    
    def __unicode__(self):
        return self.id


class image_documents(models.Model):
    app_form= models.ForeignKey(Applicationform, on_delete=models.CASCADE,blank=True,null=True,related_name = 'app_image')

    signature_img = models.CharField(max_length=200,default='no_image.png')
    revenue_approval = models.CharField(max_length=200,default='no_image.png')
    declaration = models.CharField(max_length=200,default='no_image.png')
    revenue_application = models.CharField(max_length=200,default='no_image.png')
    location_sktech = models.CharField(max_length=200,default='no_image.png')
    tree_ownership_detail = models.CharField(max_length=200,default='no_image.png')
    aadhar_detail = models.CharField(max_length=200,default='no_image.png')

    
    def __unicode__(self):
        return self.id

class TransitPass(models.Model):
    app_form= models.ForeignKey(Applicationform, on_delete=models.CASCADE,blank=True,null=True,related_name = 'transitpass_app')

    qr_code = models.CharField(max_length=200,blank=True,null=True)
    qr_code_img = models.CharField(max_length=200,blank=True,null=True)
    vehicle_reg_no = models.CharField(max_length=100,blank=True,null=True)
    driver_name = models.CharField(max_length=200,blank=True,null=True)
    driver_phone = models.CharField(max_length=20,blank=True,null=True)
    mode_of_transport = models.CharField(max_length=200,blank=True,null=True)
    license_image = models.CharField(max_length=200,blank=True,null=True)
    photo_of_vehicle_with_number = models.CharField(max_length=200,blank=True,null=True)
    verification_status = models.BooleanField(default=False)
    state = models.CharField(max_length=255,blank=True,default='')
    district = models.CharField(max_length=255,blank=True)
    taluka = models.CharField(max_length=255,blank=True)
    block = models.CharField(max_length=255,blank=True)
    village = models.CharField(max_length=255,blank=True)
    created_date = models.DateField(auto_now_add=True)
    qr_url = models.CharField(max_length=200,blank=True,null=True)
    def __unicode__(self):
        return self.id

class RoleMethod(models.Model):
    parent = models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True,related_name = 'rolemethod_parent')
    method_name = models.CharField(blank=True,max_length=250,null=True)
    name = models.CharField(blank=True,max_length=150)
    types = models.CharField(blank=True,max_length=150,default=True)
    is_delete = models.BooleanField(default=True)
    active = models.BooleanField(default=False)

class RolePermission(models.Model):
    group = models.ForeignKey(Group,on_delete=models.CASCADE,blank=True,null=True,related_name = 'role_group')
    method = models.ForeignKey(RoleMethod,on_delete=models.CASCADE)
    created_date =models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name = 'role_created_by')
    



class District(models.Model):
    district_name = models.CharField(max_length=200,default='')

    
    def __unicode__(self):
        return self.id
        
class Taluka(models.Model):
    dist = models.ForeignKey(District,on_delete=models.CASCADE,blank=True,null=True,related_name = 'District')
    taluka_name = models.CharField(max_length=200,default='')

    
    def __unicode__(self):
        return self.id
        
class Village(models.Model):
    taluka = models.ForeignKey(Taluka,on_delete=models.CASCADE,blank=True,null=True,related_name = 'Taluka')
    village_name = models.CharField(max_length=200,default='')

    
    def __unicode__(self):
        return self.id