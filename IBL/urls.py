from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from firstapp import views as user_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),
    path('',user_views.utloan, name='utloan'),
    path('terms_conditions/',user_views.terms_conditions, name='terms_conditions'),
    path('home/', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    url(r'^validate_username/$', user_views.validate_username, name='validate_username'),
    url(r'^validate_mail/$', user_views.validate_mail, name='validate_mail'),
    path('login/', user_views.login, name='login'),
    path('logout/',user_views.logout,name='logout'),
    path('bsdetails/', user_views.bsdetails, name='bsdetails'),
    path('advdetails/', user_views.advdetails, name='advdetails'),
    path('reasons/', user_views.reasons, name='reasons'),
    path('invoiceform/', user_views.invdetails, name='invdetails'),
    path('cdetails/', user_views.cdetails, name='cdetails'),
    path('loanhistory/', user_views.loan_history, name='loan_history'),

    path('er_diagram/',user_views.er_diagram,name='er_diagram'),
    path('process_map/',user_views.process_map,name='process_map'),

    url(r"^inv_details/verifycustomersloastatus/(?P<bid>[0-9]+)/(?P<loan_id>[0-9]+)/(?P<cid>[0-9]+)/$", user_views.verifycustomersloastatus, name='verifycustomersloastatus'),
    url(r"^inv_details/verifybusinessloastatus/(?P<bid>[0-9]+)/(?P<loan_id>[0-9]+)/$", user_views.verifybusinessloastatus, name='verifybusinessloastatus'),
    url(r"^repayment/(?P<vpa>[0-9a-zA-Z]+)/(?P<loan_id>[0-9]+)/(?P<c_id>[0-9]+)/$", user_views.repayment, name='repayment'),

    path('employeelogin/', user_views.Employee_login, name='employeelogin'),
    path('employeelogout/', user_views.Employee_logout, name='employeelogout'),
    path('CSinterface/',user_views.CSinterface,name='CSinterface'),
    path('Staffinterface/',user_views.Staffinterface,name='Staffinterface'),
    path('managerinterface', user_views.managerinterface, name='managerinterface'),

    path('investor_interface/', user_views.investor_interface, name='investor_interface'),
    path('investor_register/', user_views.investor_register, name='investor_register'),
    path('investor_login/', user_views.investor_login, name='investor_login'),
    path('investor_logout/', user_views.investor_logout, name='investor_logout'),

    path('forgot_password/', user_views.forgot_password, name='forgot_password'),
    url(r"^reset/(?P<email>[0-9A-Za-z@.]+)/(?P<token>[0-9A-Za-z]+)/$", user_views.password_reset_confirm, name='password_reset_confirm'),
    ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)