from django.contrib import admin
from firstapp.models import UTEmployees, Business, Business_Loan_Application, Customer, CustomerService_Details_Business, \
    CustomerService_Details_Customer, Staff_Details_Business, Staff_Details_Customer, Manager, Business_Verification, \
    Customer_Verification, VirtualPayment, Disbursement, Accepted_Customers, Accepted_Business, Investor, Investor_mapping, \
    UT_Earnings, Collection, Mapping_values, Rejected_Loans, BlackListed
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class EmployeeInline(admin.StackedInline):
    model = UTEmployees
    can_delete = False
    verbose_name_plural = 'employee'


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UTEmployees)
admin.site.register(Business)
admin.site.register(Business_Loan_Application)
admin.site.register(Customer)
admin.site.register(CustomerService_Details_Business)
admin.site.register(CustomerService_Details_Customer)
admin.site.register(Staff_Details_Business)
admin.site.register(Staff_Details_Customer)
admin.site.register(Manager)
admin.site.register(Business_Verification)
admin.site.register(Customer_Verification)
admin.site.register(VirtualPayment)
admin.site.register(Disbursement)
admin.site.register(Accepted_Customers)
admin.site.register(Accepted_Business)
admin.site.register(Investor)
admin.site.register(Investor_mapping)
admin.site.register(UT_Earnings)
admin.site.register(Collection)
admin.site.register(Mapping_values)
admin.site.register(Rejected_Loans)
admin.site.register(BlackListed)
