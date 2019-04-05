from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class UTEmployees(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=20, null=True)


class Business(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    b_id = models.AutoField(primary_key=True)
    b_name = models.CharField(max_length=30, blank=True)
    b_owner_name = models.CharField(max_length=30, blank=True)
    b_email = models.EmailField(default='a@example.com')
    b_contact = models.BigIntegerField(default=0)
    b_addr = models.TextField(blank=True)
    b_pan_no = models.CharField(max_length=10, unique=True)
    b_est_date = models.DateField()
    b_type = models.CharField(max_length=20, blank=True)
    b_applied_date = models.DateTimeField(default=datetime.now())
    adv_details = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return str(self.b_name)

class Business_Loan_Application(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.AutoField(primary_key=True)
    b_turnover = models.DecimalField(default=0, decimal_places=2, max_digits=14, blank=True, null=True)
    b_total_invoice_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14, blank=True, null=True)
    b_no_of_invoices = models.BigIntegerField(blank=True, null=True)
    b_audit_path = models.TextField(blank=True, null=True)
    b_ledger_path = models.TextField(blank=True, null=True)
    b_status = models.CharField(max_length=30, default='NA')
    loan_status = models.CharField(max_length=30, default='Active')
    applied_date = models.DateTimeField(default=datetime.now())
    b_reason_to_apply = models.CharField(max_length=30, blank=True)
    # b_reject_case = models.CharField(max_length=30)

    def __str__(self):
        return str(self.b_turnover)

class Customer(models.Model):
    c_id = models.AutoField(primary_key=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    c_num = models.IntegerField(default=0, null=True)
    c_owner_name = models.CharField(max_length=30, null=True)
    cb_name = models.CharField(max_length=30, null=True)
    # c_contact = models.BigIntegerField(default=0)
    cb_contact = models.BigIntegerField(default=0, null=True)
    cb_email = models.CharField(max_length=40, null=True)
    cb_address = models.CharField(max_length=150, null=True)
    cb_type = models.CharField(max_length=30, null=True)
    cb_relation = models.IntegerField(default=0, null=True)
    # c_pan_no = models.CharField(max_length=20)
    cb_pan_no = models.CharField(max_length=20, null=True)
    cb_est_date = models.DateField(blank=True, null=True)
    cb_turnover = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    cb_invoice_no = models.BigIntegerField(default=0, null=True)
    cb_invoice_amt = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    c_issue_date = models.DateField(null=True)
    c_due_date = models.DateField(null=True)
    c_stored_date = models.DateTimeField(default=datetime.now)
    c_file_audit = models.TextField(blank=True)
    c_sales_ledger = models.TextField(blank=True)
    c_file_invoice = models.TextField(blank=True)
    c_file_statement = models.TextField(blank=True)
    is_filled = models.IntegerField(default=0)

    def __str__(self):
        return str(self.cb_name)


class CustomerService_Details_Business(models.Model):
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    b_email = models.CharField(max_length=40, null=True)
    b_contact = models.BigIntegerField(default=0, null=True)
    phonecall_status = models.CharField(max_length=20, default='Pending')
    address_status = models.CharField(max_length=20, default='Pending')
    reverification = models.CharField(max_length=30, default='No')
    cs_status = models.CharField(max_length=20, default='Pending')
    cs_remarks = models.TextField(default='None', blank=True)


class CustomerService_Details_Customer(models.Model):
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    c_owner_name = models.CharField(max_length=30, null=True)
    cb_name = models.CharField(max_length=30, null=True)
    cb_type = models.CharField(max_length=30, null=True)
    cb_invoice_amt = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    cb_email = models.CharField(max_length=40, null=True)
    cb_contact = models.BigIntegerField(default=0, null=True)
    phonecall_status = models.CharField(max_length=20, default='Pending')
    address_status = models.CharField(max_length=20, default='Pending')
    cs_status = models.CharField(max_length=20, default='Pending')
    cs_remarks = models.TextField(default='None')


class Staff_Details_Business(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    b_st_file_audit = models.TextField(blank=True)
    b_st_sales_ledger = models.TextField(blank=True)
    b_st_status = models.CharField(max_length=20, default='Pending')
    b_st_remarks = models.TextField(default='None')


class Staff_Details_Customer(models.Model):
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    cb_invoice_amt = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    st_file_audit = models.TextField(blank=True)
    st_sales_ledger = models.TextField(blank=True)
    st_file_invoice = models.TextField(blank=True)
    st_file_statement = models.TextField(blank=True)
    st_status = models.CharField(max_length=20, default='Pending')
    st_remarks = models.TextField(default='None')

class Manager(models.Model):
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    m_status = models.CharField(max_length=50, null=True)
    reverify = models.CharField(max_length=30, default="No")
    remarks = models.CharField(max_length=30, null=True)

# Verification Table
class Business_Verification(models.Model):
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    ml_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    ml_status = models.CharField(max_length=50, default='Not yet Started')
    ml_remarks = models.TextField(default='Not yet Verified')
    mv_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    mv_status = models.CharField(max_length=50, default='Not yet Started')
    mv_remarks = models.TextField(default='Not yet Verified')
    mv_reverify = models.TextField(default='No', blank=True, null=True, max_length=20)
    final_status = models.CharField(default='Pending', max_length=30)
    requested_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    sanctioned_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    loa_status = models.CharField(default='Not Yet Sent', max_length=20)


class Customer_Verification(models.Model):
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    ml_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    ml_status = models.CharField(max_length=50, default="Not yet Started")
    ml_remarks = models.TextField(default='Not yet Verified')
    mv_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    mv_status = models.CharField(max_length=50, default='Not yet Started')
    mv_remarks = models.TextField(default='Not yet Verified')
    mv_reverify = models.TextField(default='No', blank=True, null=True, max_length=20)
    final_status = models.CharField(default='Pending', max_length=30)
    loa_status = models.CharField(default='Not Yet Sent', max_length=20)


class VirtualPayment(models.Model):
    # vp_id = models.AutoField(primary_key=True)
    vpa = models.CharField(max_length=20, primary_key=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    created_date = models.DateTimeField(default=datetime.now(), blank=True)
    # paid_date = models.DateTimeField(blank=True)
    expiry_date = models.DateTimeField(blank=True)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    # status = models.CharField(default='UnPaid', max_length=20)

class Disbursement(models.Model):
    disburse_id = models.AutoField(primary_key=True)
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    disburse_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    disburse_date = models.DateTimeField(default=datetime.now())
    vpa = models.CharField(max_length=20, null=True)
    status = models.TextField(blank=True)

class Accepted_Customers(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    c_owner_name = models.CharField(max_length=30, null=True)
    cb_name = models.CharField(max_length=30, null=True)
    cb_contact = models.BigIntegerField(default=0, null=True)
    cb_email = models.CharField(max_length=40, null=True)
    cb_address = models.CharField(max_length=150, null=True)
    cb_type = models.CharField(max_length=30, null=True)
    cb_relation = models.IntegerField(default=0, null=True)
    cb_pan_no = models.CharField(max_length=20, null=True)
    cb_est_date = models.DateField(blank=True, null=True)
    cb_turnover = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    cb_invoice_no = models.BigIntegerField(default=0, null=True)
    cb_invoice_amt = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    c_issue_date = models.DateField(null=True)
    c_due_date = models.DateField(null=True)
    c_stored_date = models.DateTimeField(default=datetime.now)
    c_file_audit = models.TextField(blank=True)
    c_sales_ledger = models.TextField(blank=True)
    c_file_invoice = models.TextField(blank=True)
    c_file_statement = models.TextField(blank=True)
    ml_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    ml_status = models.CharField(max_length=50, default="Not yet Started")
    ml_remarks = models.TextField(default='Not yet Verified')
    mv_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    mv_status = models.CharField(max_length=50, default='Not yet Started')
    mv_remarks = models.TextField(default='Not yet Verified')
    mv_reverify = models.TextField(default='No', blank=True, null=True, max_length=20)
    final_status = models.CharField(default='Pending', max_length=30)
    loa_status = models.CharField(default='Not Yet Sent', max_length=20)
    phonecall_status = models.CharField(max_length=20, default='Pending')
    address_status = models.CharField(max_length=20, default='Pending')
    cs_remarks = models.TextField(default='None')
    st_file_audit = models.TextField(blank=True)
    st_sales_ledger = models.TextField(blank=True)
    st_file_invoice = models.TextField(blank=True)
    st_file_statement = models.TextField(blank=True)
    st_remarks = models.TextField(default='None')
    invoice_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    repaid_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    due_date = models.DateField(null=True, blank=True)
    repaid_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True)
    pay_link = models.TextField(null=True, blank=True)


class Accepted_Business(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    b_name = models.CharField(max_length=30, blank=True)
    b_owner_name = models.CharField(max_length=30, blank=True)
    b_email = models.EmailField(default='a@example.com')
    b_contact = models.BigIntegerField(default=0)
    b_addr = models.TextField(blank=True)
    b_pan_no = models.CharField(max_length=10)
    b_est_date = models.DateField()
    b_type = models.CharField(max_length=20, blank=True)
    b_applied_date = models.DateTimeField(default=datetime.now())
    adv_details = models.CharField(max_length=40, blank=True)
    b_turnover = models.DecimalField(default=0, decimal_places=2, max_digits=14, blank=True, null=True)
    b_required_loan_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14, blank=True, null=True)
    b_no_of_invoices = models.BigIntegerField(blank=True, null=True)
    b_audit_path = models.TextField(blank=True, null=True)
    b_ledger_path = models.TextField(blank=True, null=True)
    b_status = models.CharField(max_length=30, default='NA')
    loan_status = models.CharField(max_length=30, default='Active')
    applied_date = models.DateTimeField(default=datetime.now())
    b_reason_to_apply = models.CharField(max_length=30, blank=True)
    b_st_file_audit = models.TextField(blank=True)
    b_st_sales_ledger = models.TextField(blank=True)
    b_st_status = models.CharField(max_length=20, default='Pending')
    b_st_remarks = models.TextField(default='None')
    ml_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    ml_status = models.CharField(max_length=50, default='Not yet Started')
    ml_remarks = models.TextField(default='Not yet Verified')
    mv_accuracy = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    mv_status = models.CharField(max_length=50, default='Not yet Started')
    mv_remarks = models.TextField(default='Not yet Verified')
    mv_reverify = models.TextField(default='No', blank=True, null=True, max_length=20)
    final_status = models.CharField(default='Pending', max_length=30)
    requested_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    loa_status = models.CharField(default='Not Yet Sent', max_length=20)
    sanctioned_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    one_disburse_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    one_disburse_date = models.DateTimeField(blank=True, null=True, default=None)
    one_disburse_id = models.CharField(max_length=30, null=True)
    two_disburse_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    two_disburse_date = models.DateTimeField(blank=True, null=True, default=None)
    two_disburse_id = models.CharField(max_length=30, null=True)
    status = models.CharField(max_length=30)


class Investor(models.Model):
    investor_id = models.CharField(max_length=15, primary_key=True)
    inv_user = models.CharField(max_length=30, unique=True, blank=True)
    investor_mail_id = models.EmailField(max_length=256)
    investor_phone_number = models.CharField(max_length=12)
    invested_date = models.DateTimeField(default=datetime.now, blank=True)
    investment_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    available_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    disbursement_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    investor_profit = models.DecimalField(default=0, decimal_places=2, max_digits=14)

class Investor_mapping(models.Model):
    investor_id = models.ForeignKey(Investor, on_delete=models.CASCADE)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    disbursement_date = models.DateTimeField(default=datetime.now, blank=True)
    investor_profit = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    status = models.CharField(max_length=15)

class UT_Earnings(models.Model):
    investor_id = models.ForeignKey(Investor, on_delete=models.CASCADE, blank=True)
    b_id = models.ForeignKey(Accepted_Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    profit_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)

class Collection(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    c_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    invoice_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    repayment_amount = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    due_date = models.DateField(null=True, blank=True)

class Mapping_values(models.Model):
    investor_map_value = models.IntegerField(default=1)

class Rejected_Loans(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True)
    loan_id = models.ForeignKey(Business_Loan_Application, on_delete=models.CASCADE, blank=True)
    status = models.CharField(max_length=30, null=True)
    remarks = models.TextField(default='None')

class BlackListed(models.Model):
    b_id = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True, null=True)
    b_pan_no = models.CharField(max_length=10)
