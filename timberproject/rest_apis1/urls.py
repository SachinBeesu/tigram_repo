from knox.views import LogoutView
from django.urls import path,include
from .views import *
from rest_framework import routers
from rest_apis import views
# LoginAPI

urlpatterns = [
path('auth/', include('knox.urls')),
path('auth/LoginAPI',LoginAPI.as_view()),
path('auth/NewLogin',NewLogin.as_view()),
path('auth/NewRegisterAPI',NewRegisterAPI.as_view()),
path('auth/RegisterAPI',RegisterAPI.as_view()),
path('auth/OtpVerify',OtpVerify.as_view()),
path('auth/forgotpassword',ForgotPassword.as_view()),
path('auth/forgotverifyotp',ForgotOtpVerify.as_view()),
path('auth/changepassword',ChangeForgotPasswordView.as_view()),
path('auth/InsertRecord',InsertRecord.as_view()),
path('auth/ListViewApplication',ListViewApplication.as_view()),
path('auth/EditProfile', EditProfile.as_view()),
path('auth/ViewProfile', ViewProfile.as_view()),
# 
path('auth/new_transit_pass_pdf/<int:applicant_no>/', new_transit_pass_pdf,name='new_transit_pass_pdf'),
path('auth/new_user_report/<int:applicant_no>/', new_user_report,name='new_user_report'),
path('auth/qr_code_pdf/<int:applicant_no>/', qr_code_pdf,name='qr_code_pdf'),
path('auth/summary_report/', summary_report,name='summary_report'),

path('auth/ApprovedListViewApplication',ApprovedListViewApplication.as_view()),

path('auth/PendingListViewApplication',PendingListViewApplication.as_view()),


path('auth/approve_transit_pass', approve_transit_pass.as_view(),name='approve_transit_pass'),

path('auth/UpdateVehicle',UpdateVehicle.as_view()),
path('auth/UpdateTimberlog',UpdateTimberlog.as_view(),name='UpdateTimberlog'),

path('auth/UpdateVehicle2/<int:app_id>/',UpdateVehicle2.as_view(),name='UpdateVehicle2'),


path('auth/ViewApplication',ViewApplication.as_view()),

path('auth/ListRange',ListRange.as_view()),
path('auth/LoadDivision',LoadDivision.as_view()),

path('auth/dashbord_chart',dashbord_chart.as_view()),

path('auth/dashbord_AppList',dashbord_AppList.as_view()),



path('auth/table_one/', views.table_one.as_view(),name='tabel_one'),
path('auth/table_two/', views.table_two.as_view(),name='tabel_two'),
path('auth/table_three/', views.table_three.as_view(),name='tabel_three'),

path('auth/table_four/', views.table_four.as_view(),name='tabel_four'),
path('auth/table_five/', views.table_five.as_view(),name='table_five'),

path('auth/table_six/', views.table_six.as_view(),name='table_six'),

path('auth/table_seven/', views.table_seven.as_view(),name='table_seven'),
path('auth/table_eight/', views.table_eight.as_view(),name='table_eight'),

path('auth/table_nine/', views.table_nine.as_view(),name='table_nine'),






















path('auth/logout', LogoutView.as_view(), name='knox_logout'),
]