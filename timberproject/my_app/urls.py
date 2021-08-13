from django.urls import path,include
from .views import *
from django.conf.urls import url
from my_app import views
from apscheduler.schedulers.background import BackgroundScheduler
import threading
scheduler = BackgroundScheduler()
scheduler.start()
urlpatterns = [
    path('', index,name='index'),
    path('login/', user_login,name='user_login'),
    path('staff_login/', staff_login,name='staff_login'),
    path('admin/', admin_login,name='admin_login'),
    # path('admin/admin/', super_login,name='super_login'),
    path('dashboard/',dashboard,name='dashboard'),
    path('forgot_password/', forgot_password,name='forgot_password'),
    path('Otp_verify/', Otp_verify,name='Otp_verify'),
    path('get_log_qr_details/<int:app_id>',get_log_qr_details,name='get_log_qr_details'),
    path('newpassword/', set_newpassword,name='newpassword'),

    #Admin
    path('admin/dashboard/',admin_dashboard,name='admin_dashboard'),
    path('admin/admin_logout/', admin_logout,name='admin_logout'),
    # admin_dashboard
    path('admin/view_users/',view_users,name='admin_view_users'),
    path('admin/load_division/',load_division,name='admin_load_division'),
    path('admin/load_taluka/',load_taluka,name='admin_load_taluka'),
    path('admin/load_village/',load_village,name='admin_load_village'),

    path('admin/update_users/<int:user_id>/',update_users,name='admin_update_users'),
    path('admin/delete_users/',delete_users,name='admin_delete_users'),
    path('admin/view_deputy_officers/',view_deputy_officers,name='admin_view_deputy_officers'),
    path('admin/view_revenue_officers/',view_revenue_officers,name='admin_view_revenue_officers'),
    path('admin/add_revenue_officers/',add_revenue_officers,name='admin_add_revenue_officers'),
    path('admin/add_forest_range_officers/',add_forest_range_officers,name='admin_add_forest_range_officers'),
    path('admin/add_deputy_range_officers/',add_deputy_range_officers,name='admin_add_deputy_range_officers'),
    path('admin/update_deputy_range_officers/<int:user_id>/',update_deputy_range_officers,name='admin_update_deputy_range_officers'),
    path('admin/update_revenue_officers/<int:user_id>/',update_revenue_officers,name='admin_update_revenue_officers'),
    path('admin/update_forest_range_officers/<int:user_id>/',update_forest_range_officers,name='admin_update_forest_range_officers'),
    path('admin/add_division_officers/',add_division_officers,name='admin_add_division_officers'),
    path('admin/view_division_officers/',view_division_officers,name='admin_view_division_officers'),
    path('admin/update_division_officers/<int:user_id>/',update_division_officers,name='admin_update_division_officers'),
    path('admin/add_field_officers/',add_field_officers,name='admin_add_field_officers'),
    path('admin/view_field_officers/',view_field_officers,name='admin_view_field_officers'),
    path('admin/update_field_officers/<int:user_id>/',update_field_officers,name='admin_update_field_officers'),
    path('admin/add_state_officers/',add_state_officers,name='admin_add_state_officers'),
    path('admin/view_state_officers/',view_state_officers,name='admin_view_state_officers'),
    path('admin/update_state_officers/<int:user_id>/',update_state_officers,name='admin_update_state_officers'),

    path('admin/view_forest_officers/',view_forest_officers,name='admin_view_forest_officers'),
    path('admin/roles/roles_list/',roles_list,name='admin_roles_list'),
    path('admin/roles/add_role/',add_role,name='admin_add_role'),
    path('admin/roles/edit_role/<int:grp_id>/',edit_role,name='admin_edit_role'),
    path('admin/roles/delete_roles/',delete_roles,name='delete_roles'),
    path('admin/roles/delete_role/<int:role_id>/',delete_role,name='delete_role'),

    path('admin/permissions/permissions_list/',role_permission_list,name='admin_permissions'),
    path('admin/permissions/edit_permissions/<int:role_id>',edit_role_permission,name='admin_edit_permissions'),
    path('admin/permissions/save_role_permission/',save_role_permission,name='admin_save_role_permission'),
    path('admin/permissions/view_role_permission/<int:role_id>',view_role_permission,name='view_role_permission'),
    #path('admin/permissions/edit_individual_user_permission/<int:user_id>',edit_individual_user_permission,name='edit_individual_user_permission'),

    path('admin/detail_view_users/<int:user_id>/',detail_view_users,name='detail_view_users'),
    path('admin/detail_view_officer/<int:user_id>/<str:officer_type>',detail_view_officer,name='detail_view_officer'),
    path('admin/delete_user/<int:user_id>/',delete_user,name='delete_user'),

    path('admin/division/add_division/',add_division,name='add_division'),
    path('admin/division/view_divisions/',view_divisions,name='view_divisions'),
    path('admin/division/edit_division/<int:div_id>/',edit_division,name='edit_division'),
    path('admin/division/delete_division/<int:div_id>/',delete_division,name='delete_division'),
    path('admin/division/delete_divisions/',delete_divisions,name='delete_divisions'),

    path('admin/division/add_range/',add_range,name='add_range'),
    path('admin/division/view_ranges/',view_ranges,name='view_ranges'),
    path('admin/division/edit_range/<int:range_id>/',edit_range,name='edit_range'),
    path('admin/division/delete_range/<int:range_id>/',delete_range,name='delete_range'),
    path('admin/division/delete_ranges/',delete_ranges,name='delete_ranges'),
    # path('admin/division/view_ranges/',view_ranges,name='view_ranges'),

    path('admin/species/add_species/',add_tree_species,name='add_species'),
    path('admin/species/view_species/',view_tree_species,name='view_species'),
    path('admin/species/edit_species/<int:speci_id>/',edit_tree_species,name='edit_species'),
    path('admin/species/delete_speci/<int:speci_id>/',delete_tree_speci,name='delete_speci'),
    path('admin/species/delete_species/',delete_tree_species,name='delete_species'),


    # path('staff_dashboard/',officer_dashboard,name='officer_dashboard'),
    # path('staff_dashboard/',officer_dashboard,name='officer_dashboard'),    



    path('staff_dashboard/',officer_dashboard,name='officer_dashboard'),
    path('pending_applications/',pending_applications,name='pending_applications'),
    path('approved_applications/',approved_applications,name='approved_applications'),
    path('view_profile/<int:user_id>/',view_profile,name='view_profile'),
    path('edit_profile/<int:user_id>/',edit_profile,name='edit_profile'),
    path('logout/', user_logout,name='user_logout'),
    path('registration/', signup,name='signup'),
    path('apply_transit_pass/', application_form,name='application_form'),
    path('apply_noc/', noc_application_form,name='noc_application_form'),
    path('apply_notified/', notified_application_form,name='notified_application_form'),
    path('update_vehicle/<int:app_id>/', update_vehicle,name='update_vehicle'),
    path('update_timberlog/<int:applicant_no>/', update_timberlog,name='update_timberlog'),
    path('load_timberlog/<int:applicant_no>/', load_timberlog,name='load_timberlog'),
    path('list_of_application/', application_list,name='application_list'),
    path('reject_reason/', reject_reason,name='reject_reason'),
    path('all_reports/', all_reports,name='all_reports'),
    path('no_of_applicantions/', no_of_applicantions,name='no_of_applicantions'),
    path('species_wise_transport/', species_wise_transport,name='species_wise_transport'),
    path('trees_transport/', trees_transport,name='trees_transport'),
    path('species_wise_dest_transport/', species_wise_dest_transport,name='species_wise_dest_transport'),
    path('total_volume_dest/', total_volume_dest,name='total_volume_dest'),
    path('approval_time_report/', approval_time_report,name='approval_time_report'),
    path('trees_cutted_report/', trees_cutted_report,name='trees_cutted_report'),
    path('cutting_reasons_report/', cutting_reasons_report,name='cutting_reasons_report'),#TO BE EDIT
    path('application_details/<int:app_id>/', application_view,name='application_view'),
    path('userapplication_details/<int:app_id>/', application_userview,name='application_userview'),
    path('application_useredit/<int:app_id>/', application_useredit,name='application_useredit'),
    path('edit_application/<int:app_id>/', edit_application,name='edit_application'),
    path('approve_transit_pass/<int:app_id>/', approve_transit_pass,name='approve_transit_pass'),
    path('check_status/', check_status,name='check_status'),
    # path('load_tree_species/', load_tree_species,name='load_tree_species'),
    path('transit_pass_pdf/<int:applicant_no>/', transit_pass_pdf,name='transit_pass_pdf'),
    path('qr_code_pdf/<int:applicant_no>/', qr_code_pdf,name='qr_code_pdf'),
    path('scanqr/<str:code>/', scanqr,name='scanqr'),
    path('scan_logqr/<str:code>/', scan_logqr,name='scan_logqr'),
    path('log_qrcode_pdf/<int:log_no>/', log_qrcode_pdf,name='log_qrcode_pdf'),
    path('user_report/<int:applicant_no>/', user_report,name='user_report'),
    path('summary_report/', summary_report,name='summary_report'),
    path('view_summary_report/', view_summary_report,name='view_summary_report'),
    path('noc_report/', noc_report,name='noc_report'),
    path('queries/', query,name='query'),

    path('admin/vpassword/', admin_vpassword,name='admin_vpassword'),
    path('admin/admin_password/', admin_password,name='admin_password'),

    # (?# url(r'^transit_pass_pdf/(?P<app_id>\d+)/$', transit_pass_pdf, name='transit_pass_pdf'),)
    # path('add_asset/', add_asset,name='add_asset'),
]


scheduler.add_job(views.test_sample,'interval',minutes=1)
scheduler.add_job(views.approve_deemed,'interval',minutes=2)