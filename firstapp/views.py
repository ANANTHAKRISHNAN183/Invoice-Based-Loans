from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse
from firstapp.models import UTEmployees, Business, Business_Loan_Application, Customer, \
    CustomerService_Details_Business, CustomerService_Details_Customer, Staff_Details_Business, Staff_Details_Customer, Manager, Business_Verification, \
    Customer_Verification, VirtualPayment, Disbursement, Accepted_Customers, Accepted_Business, Investor, Investor_mapping, \
    UT_Earnings, Mapping_values, Rejected_Loans, BlackListed
from django.contrib.auth import authenticate
from django.contrib import auth
from . decorators import user_not_loggedin, cs_not_loggedin, staff_not_loggedin, manager_not_loggedin, investor_not_loggedin
from django.core.files.storage import FileSystemStorage
from django.db.models import Max, Q
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.http import JsonResponse
import time
import random
import decimal



def er_diagram(request):
    return render(request,'Documents/er_diagram.html')
def process_map(request):
    return render(request,'Documents/process_map.html')


# Application Home Page
def utloan(request):
    if request.method == 'POST' and 'user' in request.POST:
        return redirect('terms_conditions')
    elif request.method == 'POST' and 'investor' in request.POST:
        return redirect('investor_register')
    elif request.method == 'POST' and 'employee' in request.POST:
        return redirect('employeelogin')
    else:
        return render(request, 'utloan.html')

# T&C Page for User registration
def terms_conditions(request):
    if request.method == 'POST':
        return redirect('register')
    else:
        return render(request, 'terms&conditions.html')

# Storing details from User Registration Form
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username)
        if user:
            message = 'User details already Exists!'
            return render(request, 'Registration_Login/register.html', {'message': message})
        else:
            email = request.POST.get('email')
            pwd = request.POST.get('pass')
            u = User(username=username, email=email)
            u.set_password(pwd)
            u.save()
            emp = UTEmployees()
            emp.user = u
            emp.department = "Business"
            emp.save()
            request.session['uname'] = username
            return redirect('home')
    else:
        return render(request, 'Registration_Login/register.html', {'user': ''})

# While registration checking if Username already exists
def validate_username(request):
    username = request.GET.get('username')
    data = {
        'is_taken': User.objects.filter(username=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Username Not Available/ Username already exists!!'
    return JsonResponse(data)

# While registration checking if Email already exists
def validate_mail(request):
    email = request.GET.get('email')
    data = {
        'is_taken': User.objects.filter(email=email).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Email address already exists!'
    return JsonResponse(data)

# User Login Authentication
def login(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        try:
            uid = User.objects.get(username=uname)
        except User.DoesNotExist:
            return render(request, 'Registration_Login/login.html', {'message': 'A User with that Credentials does not exists!!', 'user': ''})
        psw = request.POST.get("password")
        # Authenticating user
        u = authenticate(username=uname, password=psw)
        if u is not None:
            request.session['uname'] = uname
            ut = UTEmployees.objects.get(user=uid)
            if ut.department == 'Business':
                return redirect('home')
        else:
            return render(request, 'Registration_Login/login.html', {'message': 'Invalid Credentials, Please try again with valid details', 'user': ''})
    else:
        return render(request, 'Registration_Login/login.html', {'user': ''})

def logout(request):
    auth.logout(request)
    request.session.clear()
    return render(request, 'Registration_Login/logout.html', {'user': ''})

def forgot_password(request):
    message = ''
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        u = User.objects.filter(email=email, username=username)
        if u.count() == 1:
            u = User.objects.get(email=email)
            toaddress = [email]
            text = "To initiate the password reset process for your account: "+str(u.username)+" Please click the link below:<br/>"
            text += 'http://localhost:8000/reset/' + str(email)+'/'+str(get_random_string(length=10))
            text += "<br/>If clicking the link above doesn't work, please copy and paste the URL in a new browser window instead.\n"+"Sincerely,\n Team UT\n"
            subject = 'IBL PASSWORD RESET'
            msg = EmailMessage(subject, text, '', toaddress)
            msg.content_subtype = "html"
            msg.send()
            message = 'Reset Password mail has been sent to your Registered Mail Id'
            return render(request, 'ForgotPassword/password_reset_form.html', {'message': message})
        else:
            message = 'Invalid Data'
            return render(request, 'ForgotPassword/password_reset_form.html', {'invalidmessage': message})
    else:
        request.session.clear()
        return render(request, 'ForgotPassword/password_reset_form.html', {'message': message})


def password_reset_confirm(request, email, token):
    if request.method == "POST":
        pwd = request.POST.get('pwd')
        u = User.objects.get(email=email)
        u.set_password(pwd)
        u.save()
        message = 'Your password has been set. You may go ahead and Login now.'
        return render(request, 'ForgotPassword/password_reset_form.html', {'message': message})
    else:
        message = ''
        return render(request, 'ForgotPassword/password_reset_confirm.html', {'message': message})


# User Home Page
@user_not_loggedin
def home(request):
    uid = request.session['uname']
    u = User.objects.get(username=uid)

    # Button for filling Business Details Form
    if request.method == "POST" and "business" in request.POST:
        if Business.objects.filter(user=u):
            return redirect('bsdetails')
        else:
            return redirect('bsdetails')

    # Button for applying New Invoice Loan
    elif request.method == "POST" and "loan" in request.POST:
        if Business.objects.filter(user=u):
            return redirect('reasons')
        else:
            message = 'You did not submit your Business Details. So please fill it first'
            return render(request, 'ApplyLoan/bdetails.html', {'message': message})

    # Button for viewing Loan History
    elif request.method == "POST" and "loan_history" in request.POST:
        return redirect('loan_history')

    # Current Loan Application Status
    else:
        status = ''
        if "message" in request.session:
            result = request.session["message"]
        else:
            result = 3
        try:
            b = Business.objects.get(user_id=u)
        except Business.DoesNotExist:
            status += 'Business Details'
            return render(request, 'home.html', {'user': u, 'status': status})
        if result == 1:
            bl = Business_Loan_Application.objects.filter(b_id=b)
            if bl.count() != 0:
                max_loan_id = bl.aggregate(Max('loan_id'))
                max_bl = Business_Loan_Application.objects.get(loan_id=max_loan_id["loan_id__max"])
                status += max_bl.b_status
                u.message = 'Invoice Loan Application Submitted Successfully. We will connect with you through your E-Mail'
                u.status = 'Active'
            del request.session['message']
        if result == 2:
            u.message = 'Business Details Saved Successfully'
            b = Business.objects.get(user_id=u)
            bl = Business_Loan_Application.objects.filter(b_id=b)
            status = ''
            if bl.count() != 0:
                max_loan_id = bl.aggregate(Max('loan_id'))
                max_bl = Business_Loan_Application.objects.get(loan_id=max_loan_id["loan_id__max"])
                status += max_bl.b_status
            else:
                status += 'Invoice and Customer Details'
            del request.session['message']
        if result == 3:
            b = Business.objects.get(user_id=u)
            try:
                bl = Business_Loan_Application.objects.filter(b_id=b)
                max_loan_id = bl.aggregate(Max('loan_id'))
                max_bl = Business_Loan_Application.objects.get(loan_id=max_loan_id["loan_id__max"])
                if max_bl.b_status != 'NA':
                    try:
                        c = Customer.objects.filter(loan_id=max_bl.loan_id)
                        for i in c:
                            if i.is_filled == 0:
                                status += 'Details Partially Filled'
                                break
                        else:
                            status += max_bl.b_status
                            if status == 'Paid to Collection':
                                BlackListed.objects.filter(b_pan_no=b).delete()
                    except Customer.DoesNotExist:
                        status += 'Details Partially Filled'
                else:
                    status += 'Details Partially Filled'
            except Business_Loan_Application.DoesNotExist:
                status += 'Invoice and Customer Details'

        if result == 4:
            status += 'Cannot Apply for Loan'
            del request.session['message']
        return render(request, 'home.html', {'user': u, 'status': status})


# Loan History Page
def loan_history(request):
    uid = request.session['uname']
    u = User.objects.get(username=uid)
    try:
        b = Business.objects.get(user=u)
        if Business_Loan_Application.objects.filter(b_id=b).exclude(Q(b_status='NA') | Q(b_status='Loan Application Filled')).exists():
            bl = Business_Loan_Application.objects.filter(b_id=b).exclude(Q(b_status='NA') | Q(b_status='Loan Application Filled'))
            if Accepted_Business.objects.filter(b_id=b).exists():
                ob1 = []
                ac = Accepted_Business.objects.filter(b_id=b)
                for i in bl:
                    ob2 = []
                    for j in ac:
                        if i.loan_id == j.loan_id.loan_id:
                            ob2.append(i.applied_date)
                            ob2.append(i.b_total_invoice_amount)
                            ob2.append(j.sanctioned_amount)
                            ob2.append(j.one_disburse_amount)
                            ob2.append(j.one_disburse_date)
                            ob2.append(j.two_disburse_amount)
                            ob2.append(j.two_disburse_date)
                            ob2.append(i.loan_status)
                            ob2.append(i.b_status)
                            break
                    else:
                        # If a previous loan is rejected in the verification process
                        ob2.append(i.applied_date)
                        ob2.append(i.b_total_invoice_amount)
                        ob2.append(0)
                        ob2.append(0)
                        ob2.append('NIL')
                        ob2.append(0)
                        ob2.append('NIL')
                        ob2.append(i.loan_status)
                        ob2.append(i.b_status)
                    ob1.append(ob2)
                return render(request, 'loan_history.html', {'ob1': ob1})
            else:
                ob1 = []
                for i in bl:
                    ob2 = []
                    ob2.append(i.applied_date)
                    ob2.append(i.b_total_invoice_amount)
                    ob2.append(0)
                    ob2.append(0)
                    ob2.append('NIL')
                    ob2.append(0)
                    ob2.append('NIL')
                    ob2.append(i.loan_status)
                    ob2.append(i.b_status)
                    ob1.append(ob2)
                return render(request, 'loan_history.html', {'ob1': ob1})
        else:
            message = 'No Previous Loans'
            return render(request, 'loan_history.html', {'ob1': '', 'message': message})
    except:
        message = 'No Previous Loans'
        return render(request, 'loan_history.html', {'ob1': '', 'message': message})

# Storing details from Business Details Form
def bsdetails(request):
    if request.method == "POST":
        uid = request.session['uname']
        user = User.objects.get(username=uid)
        update = False
        if Business.objects.filter(user=user).exists():
            business = Business.objects.get(user=user)
            update = True
        else:
            business = Business()
            business.user = user
        business.b_name = request.POST.get('bname')
        business.b_owner_name = request.POST.get('b_owner_name')
        business.b_email = request.POST.get('b_email')
        business.b_contact = request.POST.get('b_contact')
        business.b_addr = request.POST.get('b_addr')
        business.b_est_date=request.POST.get('b_est_date')
        business.b_type=request.POST.get('b_type')
        pan_no = request.POST.get('b_pan_no')

        if update == True:
            if pan_no==business.b_pan_no or (pan_no!=business.b_pan_no and not Business.objects.filter(b_pan_no=pan_no).exists()):
                if Accepted_Business.objects.filter(b_pan_no=business.b_pan_no).exists():
                    print("hey")
                    ab = Accepted_Business.objects.filter(b_pan_no=business.b_pan_no)
                    for i in ab:
                        i.b_name = request.POST.get('bname')
                        i.b_owner_name = request.POST.get('b_owner_name')
                        i.b_email = request.POST.get('b_email')
                        i.b_contact = request.POST.get('b_contact')
                        i.b_addr = request.POST.get('b_addr')
                        i.b_est_date = request.POST.get('b_est_date')
                        i.b_type = request.POST.get('b_type')
                        i.b_pan_no = pan_no
                        i.save()
                if BlackListed.objects.filter(b_pan_no=business.b_pan_no).exists():
                    bl = BlackListed.objects.get(b_pan_no=business.b_pan_no)
                    bl.b_pan_no = pan_no
                    bl.save()
                business.b_pan_no = pan_no
                business.save()
            else:
                request.session['pan_status'] = 're-enter PAN'
                request.method = 'GET'
                return redirect('bsdetails')
        
        elif Business.objects.filter(b_pan_no=pan_no).exists():
            request.session['pan_status'] = 're-enter PAN'
            request.method = 'GET'
            return redirect('bsdetails')
        
        else:
            business.b_pan_no = pan_no
            business.save()

        request.session['message'] = 2
        if update == False:
            return redirect('advdetails')
        else:
            return redirect('home')
    else:
        uid = request.session['uname']
        user = User.objects.get(username=uid)
        if 'pan_status' in request.session and request.session['pan_status']=='re-enter PAN':
            del request.session['pan_status']
            return render(request, 'ApplyLoan/bdetails.html',{'business':'','pan_status':'re-enter PAN as it already used'})
        if(Business.objects.filter(user=user).exists()):
            business=Business.objects.get(user=user)
            return render(request,'ApplyLoan/bdetails.html',{'business':business})
        else:
            return render(request, 'ApplyLoan/bdetails.html',{'business':''})


# UT advertisement details form
def advdetails(request):
    if request.method == "POST":
        uid = request.session['uname']
        user = User.objects.get(username=uid)
        bid = Business.objects.get(user=user)
        bid.adv_details = request.POST.get('utpromo')
        bid.save()
        return redirect('home')
    else:
        return render(request, 'ApplyLoan/advertisement.html')


# Storing Reason for applying a loan from User
@user_not_loggedin
def reasons(request):
    uid = request.session['uname']
    user = User.objects.get(username=uid)
    business = Business.objects.get(user=user)
    if request.method == "POST":
        business_l = Business_Loan_Application(b_id=business)
        reason = request.POST.get("reasons")
        business_l.b_reason_to_apply = reason
        business_l.save()
        request.session['loan_id'] = business_l.loan_id
        return redirect('invdetails')
    else:
        return render(request, 'ApplyLoan/reasons.html')


# Storing Loan Application Form Details
@user_not_loggedin
def invdetails(request):
    if request.method == "POST":
        loan_id = request.session['loan_id']
        uid = request.session['uname']
        user = User.objects.get(username=uid)
        bid = Business.objects.get(user=user)
        b_turnover = decimal.Decimal(request.POST.get('b_turnover'))
        b_total_invoice_amount = decimal.Decimal(request.POST.get('b_total_invoice_amount'))
        b_no_of_invoices = request.POST.get('b_no_of_invoices')

        invdetail = Business_Loan_Application.objects.get(loan_id=loan_id)
        invdetail.b_turnover = b_turnover
        invdetail.b_total_invoice_amount = b_total_invoice_amount
        invdetail.b_no_of_invoices = b_no_of_invoices
        invdetail.save()

        file = request.FILES['b_file_audit']
        filename = 'b_file_audit'
        fs = FileSystemStorage()
        extension = str(file).split('.')
        # Storing Local File path in the table
        b_audit_path = 'http://127.0.0.1:8000/media/' + fs.save(str(invdetail.loan_id)+'/'+str(filename) + '.' + extension[1], file)
        file = request.FILES['b_file_saleledger']
        filename = 'b_file_saleledger'
        extension = str(file).split('.')
        b_ledger_path = 'http://127.0.0.1:8000/media/' + fs.save(str(invdetail.loan_id)+'/'+str(filename) + '.' + extension[1], file)
        invdetail.b_audit_path = b_audit_path
        invdetail.b_ledger_path = b_ledger_path
        invdetail.b_status = 'Loan Application Filled'
        invdetail.save()
        for i in range(0, int(b_no_of_invoices)):
            c = Customer(c_num=i+1)
            c.loan_id = invdetail
            c.save()
        request.session['c_num'] = 0
        return redirect('cdetails')
    else:
        return render(request, 'ApplyLoan/Invoiceform.html', {})


# Storing Individual Customer details along with their documents
@user_not_loggedin
def cdetails(request):
    loan_id = request.session['loan_id']
    c_num = request.session['c_num']
    uid = request.session['uname']
    user = User.objects.get(username=uid)
    bid = Business.objects.get(user=user)
    request.session['message'] = 3
    if request.method == "POST":
        c = Customer.objects.filter(loan_id=loan_id)
        num = len(c)
        submit = request.POST['Submit']
        cu = Customer.objects.get(loan_id=loan_id, c_num=c_num+1)
        cu.c_owner_name = request.POST.get('c_owner_name')
        cu.cb_name = request.POST.get('cb_name')
        cu.cb_contact = request.POST.get('cb_contact')
        cu.cb_email = request.POST.get('cb_email')
        cu.cb_address = request.POST.get('cb_address')
        cu.cb_type = request.POST.get('c_type')
        cu.cb_relation = request.POST.get('cb_relation')
        cu.cb_pan_no = request.POST.get('c_bus_pan_no')
        cu.cb_est_date = request.POST.get('c_est_date')
        cu.cb_turnover = decimal.Decimal(request.POST.get('c_turnover'))
        cu.cb_invoice_no = request.POST.get('c_invoice_no')
        cu.cb_invoice_amt = decimal.Decimal(request.POST.get('c_invoice_amount'))
        cu.c_issue_date = request.POST.get('c_invoice_issue_date')
        cu.c_due_date = request.POST.get('c_invoice_due_date')
        fs = FileSystemStorage()
        boolval = request.FILES.get('c_file_audit', False)

        # Checking whether user has uploaded a file or not
        if boolval != False:
            file = request.FILES['c_file_audit']
            filename = 'c_file_audit'
            extension = str(file).split('.')
            c_audit_path = 'http://127.0.0.1:8000/media/' + fs.save(str(loan_id)+'/'+str(cu.c_id)+'/'+str(filename) + '.' + extension[1], file)
        else:
            # Storing file path as None if user has not uploaded audit file
            c_audit_path = 'None'

        boolval = request.FILES.get('c_file_saleledger', False)
        if boolval != False:
            file = request.FILES['c_file_saleledger']
            filename = 'c_file_saleledger'
            extension = str(file).split('.')
            c_ledger_path = 'http://127.0.0.1:8000/media/' + fs.save(str(loan_id)+'/'+str(cu.c_id)+'/'+str(filename) + '.' + extension[1], file)
        else:
            c_ledger_path = 'None'

        file = request.FILES['c_file_invoice']
        filename = 'c_file_invoice'
        extension = str(file).split('.')
        c_file_invoice_path = 'http://127.0.0.1:8000/media/' + fs.save(str(loan_id)+'/'+str(cu.c_id)+'/'+str(filename) + '.' + extension[1], file)

        boolval = request.FILES.get('c_file_statement', False)
        if boolval != False:
            file = request.FILES['c_file_statement']
            filename = 'c_file_statement'
            extension = str(file).split('.')
            c_file_statement_path = 'http://127.0.0.1:8000/media/' + fs.save(str(loan_id)+'/'+str(cu.c_id)+'/'+str(filename) + '.' + extension[1], file)
        else:
            c_file_statement_path = 'None'

        cu.c_file_audit = c_audit_path
        cu.c_sales_ledger = c_ledger_path
        cu.c_file_invoice = c_file_invoice_path
        cu.c_file_statement = c_file_statement_path
        cu.is_filled = 1
        cu.save()
        request.session['c_num'] = c_num+1
        c_num = c_num+1

        if submit == str(num):
            bl = Business_Loan_Application.objects.get(loan_id=loan_id)
            bl.b_status = 'All customers data Submitted'
            bl.save()
            sendemailbusiness(request, 7, bid.b_id, loan_id)
            verification(request, loan_id, bid, c_num)
            request.session['message'] = 1
            return redirect('home')
        else:
            return render(request, 'ApplyLoan/customer.html', {'customers': c, 'cnum': c_num+1})
    c = Customer.objects.filter(loan_id=loan_id)
    return render(request, 'ApplyLoan/customer.html', {'customers': c, 'cnum': c_num+1})

# -------- Verification Process ----------
def verification(request, loan_id, bid, c_num):
    c = Customer.objects.filter(loan_id=loan_id)
    for i in c:
        customer_verification(bid, i.c_id, loan_id, request)
    bl = Business_Loan_Application.objects.get(loan_id=loan_id)
    bl.b_status = 'Under verification'
    bl.save()
    # Customer_Verification
    cv = Customer_Verification.objects.filter(loan_id=loan_id, b_id=bid, ml_status='Accepted')
    bus = Business.objects.get(b_id=bid.b_id)
    loanid = Business_Loan_Application.objects.get(loan_id=loan_id)

    # Checking the count of Accepted Customers from ML Verification
    if cv.count() > 0:
        busverify = business_verification(bid, loan_id, request)
        if busverify == 'Accepted':
            bl.b_status = 'Verification Accepted'
            bl.save()
            for i in cv:
                i.loa_status = 'LOA Not Sent'
                i.save()
                cid = Customer.objects.get(c_id=i.c_id)
                sendemailcustomers(request, 1, bid, loan_id, cid)
        elif busverify == 'Pending':
            bv = Business_Verification.objects.get(loan_id=loanid, b_id=bus)
            bv.loa_status = 'Not yet Sent'
            bv.final_status = 'Pending'
            bv.save()
        else:
            bl.b_status = 'MV Verification Rejected'
            bl.save()
            bv = Business_Verification.objects.get(loan_id=loanid, b_id=bus)
            bv.loa_status = 'Not Yet Sent'
            bv.final_status = 'Rejected'
            bv.save()
            for i in range(c_num):
                cv[i].loa_status = 'Not Yet Sent'
                cv[i].mv_status = 'Rejected due to business'
                cv[i].save()
                cv[i].final_status = 'Rejected'
            sendemailbusiness(request, 6, bid.b_id, loan_id)

    else:
        # If all customers are rejected in ML Verification then loan is rejected
        cv = Customer_Verification.objects.filter(loan_id=loan_id, b_id=bid)
        for i in range(c_num):
            cv[i].final_status = 'Rejected'
            cv[i].save()
        bv = Business_Verification(loan_id=bl, b_id=bid, ml_accuracy=0.0, ml_remarks='Rejected due to customers ML Accuracy',
                                   mv_accuracy=0.0, mv_remarks='Rejected due to customers',
                                   requested_amount=bl.b_total_invoice_amount,
                                   sanctioned_amount=0, ml_status='Rejected due to customers ML Accuracy',
                                   loa_status='Not Yet Sent',
                                   mv_status='Rejected due to customers', final_status='Rejected')
        bv.save()

        reject = Rejected_Loans()
        reject.b_id = bid
        reject.loan_id = bl
        reject.status = 'rejected'
        reject.remarks = 'Rejected due to Customers ML Accuracy'
        reject.save()
        bl.b_status = 'Verification Rejected'
        bl.loan_status = 'Inactive'
        bl.save()
        sendemailbusiness(request, 6, bid.b_id, loan_id)


# ML Verification for all Customers of a particular loan
def customer_verification(bid, cid, loan_id, request):
    cust = Customer.objects.get(c_id=cid)
    # Business loan status is changed to- Under customers verification
    bl = Business_Loan_Application.objects.get(loan_id=loan_id)
    bl.b_status = 'Under Customers verification'
    bl.save()
    mlaccuracy = decimal.Decimal(round(random.uniform(69, 100), 1))

    cv = Customer_Verification(loan_id=bl, b_id=bid, c_id=cust, ml_accuracy=mlaccuracy, ml_status='Not Yet Verified',
                               mv_status='Not yet started', loa_status='Not Applicable')
    cv.save()
    # If ML Accuracy of a customer is above 84 then it is sent directly to Manager
    # if (cv.ml_accuracy > 84):
    #     cv.ml_status = 'Accepted'
    #     cv.mv_status = 'M'
    #     cv.mv_remarks = "ML Accuracy is High"

    if cv.ml_accuracy > 69:
        cv.ml_status = 'Accepted'
        cv.ml_remarks = "ML Completed"
        cv.mv_status = 'CS'
    else:
        cv.ml_status = 'Rejected in ML'
        cv.mv_status = 'Rejected in ML'
        cv.final_status = 'Rejected'
        sendemailcustomers(request, 2, bid, loan_id, cust)
    cv.save()
    # if cv.mv_status == 'Rejected' and cv.ml_status == 'Rejected':
    #     cv.final_status = 'Rejected'
    #     cv.save()
    #     sendemailcustomers(request, 2, bid, loan_id, cust)


def business_verification(bid, loan_id, request):
    mlaccuracy = decimal.Decimal(round(random.uniform(69, 100), 1))
    bl = Business_Loan_Application.objects.get(loan_id=loan_id)
    bl.b_status = 'Under Business verification'
    bl.save()
    bv = Business_Verification(loan_id=bl, b_id=bid, ml_accuracy=mlaccuracy, requested_amount=bl.b_total_invoice_amount,
                               sanctioned_amount=0, ml_status='Not Yet Verified', mv_status='Not Yet Started',
                               loa_status='Not Applicable')
    bv.save()
    # If Business ML Accuracy is greater than 84 then directly send LOA to Business
    # if (bv.ml_accuracy > 84):
    #     bv.ml_status = 'Accepted'
    #     customers = Customer_Verification.objects.filter(loan_id=bl,b_id=bid)
    #     for customer in customers:
    #         if customer.ml_accuracy>84:
    #             sendemailcustomers(request, 1, bid, bl, customer.c_id)
    #     bv.mv_status = 'Under LOA'
    # bv.save()

    if bv.ml_accuracy > 69:
        bv.ml_status = 'Accepted'
        bv.mv_status = 'CS'
    else:
        bv.ml_status = 'Rejected in ML'
        bv.mv_status = 'Rejected in ML'
        bv.mv_remarks = "Rejected due to ML Accuracy"
        reject = Rejected_Loans()
        reject.b_id = bid
        reject.loan_id = bl
        reject.status = 'rejected'
        reject.remarks = 'Rejected due to ML Accuracy'
        bl.b_status = 'Verification Rejected'
        bl.loan_status = 'Inactive'
        bl.save()
        reject.save()
    bv.ml_remarks = "ML Completed"
    bv.save()
    if bv.ml_status == 'Accepted' and bv.mv_status == 'Accepted':
        return 'Accepted'
    elif bv.ml_status == "Accepted" and bv.mv_status != "Accepted":
        bv.final_status = 'Pending'
        bv.save()
        return 'Pending'
    else:
        bv.final_status = 'Rejected'
        bv.save()
        return 'Rejected'


# ------E-Mail's to Business----------
# 1 Mail to business when all customers have accepted LOA
# 2 LOA Acceptance Acknowledgement mail to business
# 3 LOA Mail to business with total loan eligibility
# 4 Mail to business if he rejects LOA
# 5 Mail to business if all Customers have rejected their LOA
# 6 ML or Manual verification Rejection to business
# 7 Loan Started mail to Business
# 8 Loan Completed mail to Business
def sendemailbusiness(request, value, bid, loan_id):
    b = Business.objects.get(b_id=bid)
    toaddress = [b.b_email]
    text = ''
    subject = ''

    if value == 2:
        subject = "Acknowledgement Mail"
        text = "Greetings Sir/Madam, Thank You for accepting the Agreement. We will Shortly Disburse your Loan Amount. Thank You.\n"

    elif value == 3:
        sanct_amnt = 0
        cv = Customer_Verification.objects.filter(loan_id=loan_id)
        bv = Business_Verification.objects.get(loan_id=loan_id)
        subject = 'IBL LOA'
        text = "Hi! I Hope you are doing well.Your Loan Verification is done and Your customers with <br/>"
        for i in cv:
            c = Customer.objects.get(c_id=i.c_id.c_id)
            if i.loa_status == 'Accepted' and i.final_status == 'Pending' and i.mv_status == 'Accepted in M':
                text += 'Id and Name: ' + str(c.c_id)+','+str(c.c_owner_name)+'<br/>'
                sanct_amnt += c.cb_invoice_amt
        # bv.sanctioned_amount = sanct_amnt
        # bv.save()
        text += "<br/>have been accepted in the Loan Verification Process.\nYour Total Loan Eligibility is:"+str(sanct_amnt)+". Please find the LOA attachement below and Here is the link if you wish to give your decision "+' <a href="http://localhost:8000/inv_details/verifybusinessloastatus/'+str(bid)+'/'+str(loan_id)+'" target=_blank> Click here</a>'

    elif value == 4:
        subject = "Acknowledgement Mail"
        text = "Hi!\nI Hope you are doing well \nYou have rejected the agreement. Please create a new loan if required.\n"

    elif value == 5:
        subject = "IBL Loan Rejected"
        text = "Dear Applicant\n Your All Customers have been rejected in Loan Process. So Your Loan Application is Rejected. Please re-apply the Loan with valid details."

    elif value == 6:
        subject = "IBL Loan Rejected"
        text = "Dear Applicant \n Your Loan Application has been Rejected in Verification. Please re-apply the Loan with valid details"

    elif value == 7:
        subject = "Uangteman Loan"
        text = "Hi!<br/>I Hope you are doing well <br/>Thank you for applying for loan.<br/> Soon will let you know about the status of application.<br/>"

    elif value == 8:
        subject = "Loan Process Done"
        text = "Hi!\nI Hope you are doing well \nLoan process done.\nThank you for applying for loan.\nIt was our pleasure to work with you.\n"

    elif value == 9:
        subject = "IBL Loan status Update"
        text = "Hi!\nI Hope you are doing well. Your all customers have rejected their LOA in the Loan Process. You can now apply for a new loan.\n \n"

    msg = EmailMessage(subject, text, '', toaddress)
    msg.content_subtype = "html"
    if value == 3:
        msg.attach_file('C:\\Users\\Admin\\PyCharmProjects\\IBL\\firstapp\\templates\\LOA\\businessdoc.doc')
    msg.send()


# 1 Mail to customers to accept the LOA
# 2 Mail to business that a customer has been rejected in ML or manual verification
def sendemailcustomers(request, value, bid, loan_id, cid):
    toaddress = [cid.cb_email]
    if value == 1:
        bl = Business_Loan_Application.objects.get(loan_id=loan_id)
        subject = 'IBL Letter of Agreement'
        text = "Hi! " + cid.c_owner_name + "<br/>I Hope you are doing well <br/>Here is the link for accepting the LOA. Kindly do accept it before the Due date.<br/>"+' <a href="http://localhost:8000/inv_details/verifycustomersloastatus/'+str(bid.b_id)+'/'+str(bl.loan_id)+'/'+str(cid.c_id)+'" target=_blank> Click here</a>To provide your decision.'
        msg = EmailMessage(subject, text, '', toaddress)
        msg.attach_file('C:\\Users\\Admin\\PyCharmProjects\\IBL\\firstapp\\templates\\LOA\\customerdoc.doc')
        msg.content_subtype = "html"
        msg.send()

    if value == 2:
        c = Customer.objects.get(c_id=cid.c_id)
        bl = Business_Loan_Application.objects.get(loan_id=loan_id.loan_id)
        toaddress = [bl.b_id.b_email]
        subject = "Loan Verification Update"
        text = "Dear Applicant\n Your customer with <br/>Id: " + str(c.c_id) + "<br/> Customer Name: "+str(c.c_owner_name)+"<br/>having Invoice Amount: " + str(c.cb_invoice_amt) + ", has been rejected in the Verification Process.\nPlease wait for further updates on your Loan status.\n"
        msg = EmailMessage(subject, text, '', toaddress)
        msg.content_subtype = "html"
        msg.send()

def sendloacustomers(request, loan_id):
    bl = Business_Loan_Application.objects.get(loan_id=loan_id)
    business = Business.objects.get(b_id=bl.b_id.b_id)
    customers = Customer_Verification.objects.filter(loan_id=bl.loan_id, mv_status="LOA")
    for customer in customers:
        cid = Customer.objects.get(c_id=customer.c_id.c_id)
        sendemailcustomers(request, 1, business, bl.loan_id, cid)

# Verifying the status of Customer's LOA
def verifycustomersloastatus(request, bid, loan_id, cid):
    b = Business.objects.get(b_id=bid)
    bl = Business_Loan_Application.objects.get(loan_id=loan_id)
    c = Customer.objects.get(loan_id=loan_id, c_id=cid)
    c_num = bl.b_no_of_invoices
    cv = Customer_Verification.objects.get(loan_id=loan_id, b_id=bid, c_id=cid)
    if request.method == 'POST':
        toaddress = [c.cb_email]
        subject = 'IBL LOA'
        bv = Business_Verification.objects.get(loan_id=loan_id, b_id=bid)
        # Changing the status of LOA Accepted Customer to ST
        if request.POST.get('status') == 'Accepted':
            cv.loa_status = 'Accepted'
            cv.mv_status = 'ST'
            cv.save()
            bv.mv_status = 'ST'
            bv.save()
            text = "Hi!\nI Hope you are doing well \nThank You for accepting the agreement. This is a confirmation mail to say that you  done the acceptance.\n"
            msg = EmailMessage(subject, text, '', toaddress)
            msg.content_subtype = "html"
            msg.send()
            return HttpResponse('Thank You for accepting the LOA')
        else:
            cv.loa_status = 'Rejected'
            cv.mv_status = 'Rejected in LOA'
            cv.final_status = 'Rejected'
            cv.save()
            text = "Hi!\nI Hope you are doing well \nYou did not accept the LOA.\n"
            msg = EmailMessage(subject, text, '', toaddress)
            msg.content_subtype = "html"
            msg.send()

            # Checking if all the customers of a loan have rejected their LOA
            if Customer_Verification.objects.filter(loan_id=loan_id, final_status='Rejected').count() == c_num:
                sendemailbusiness(request, 9, bid, loan_id)
                bv.mv_status = "Rejected due to Customers LOA"
                bv.mv_remarks = "Rejected because all customers have rejected their LOA"
                bv.final_status = "Rejected"
                bl.b_status = "Verification Rejected"
                bl.loan_status = "Inactive"
                bl.save()
                bv.save()
                reject = Rejected_Loans()
                reject.b_id = b
                reject.loan_id = bl
                reject.status = 'Rejected'
                reject.remarks = 'All Customers LOA Rejected'
                reject.save()
            return HttpResponse('You have Rejected the LOA')
    if cv.mv_status == 'ST' or cv.final_status == 'Rejected':
        return HttpResponse('You have already given your opinion')
    else:
        return render(request, 'LOA/loa_acceptance_mail.html')

# Verifying Business LOA status
def verifybusinessloastatus(request, bid, loan_id):
    b1 = Business_Loan_Application.objects.get(loan_id=loan_id)
    b = Business.objects.get(b_id=bid)
    bv = Business_Verification.objects.get(loan_id=b1)
    if request.method == 'POST':
        if request.POST.get('status') == 'Accepted':
            bv.sanctioned_amount = 0
            bv.loa_status = 'Accepted'
            bv.mv_status = "LOA Accepted"
            bv.final_status = 'Accepted'
            bv.save()
            cv = Customer_Verification.objects.filter(loan_id=loan_id, b_id=b, loa_status='Accepted', mv_status='Accepted in M')
            for i in cv:
                i.final_status = 'Accepted'
                i.save()
            sendemailbusiness(request, 2, bid, loan_id)
            b1.b_status = 'Business LOA Accepted'
            b1.save()
            accepted_business(request, b, loan_id)
            return HttpResponse('Thank you for accepting the LOA.The amount will be shortly be disbursed.')
        else:
            bv.loa_status = 'Rejected by Business'
            bv.final_status = 'Rejected'
            bv.save()
            reject = Rejected_Loans()
            reject.b_id = b
            reject.loan_id = b1
            reject.status = 'Rejected'
            reject.remarks = 'Rejected in Business LOA'
            reject.save()
            cv = Customer_Verification.objects.filter(loan_id=loan_id, b_id=b)
            for i in cv:
                i.final_status = 'Rejected'
                i.mv_remarks = "Rejected because Business has rejected the final LOA"
                i.save()

            b1.b_status = 'Business LOA Rejected'
            b1.loan_status = 'Inactive'
            b1.save()
            sendemailbusiness(request, 4, bid, loan_id)
            return HttpResponse('You have rejected the loan process')
    if bv.final_status == 'Accepted' or bv.final_status == 'Rejected':
        return HttpResponse('You have already given your opinion')
    else:
        return render(request, 'LOA/loa_acceptance_mail.html')

# Employee Login Page
def Employee_login(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        try:
            uid = User.objects.get(username=uname)
        except User.DoesNotExist:
            return render(request, 'emplogin.html', {'message': 'Invalid Username. Please try again!!', 'user': ''})
        e = UTEmployees.objects.get(user=uid)
        psw = request.POST.get("password")
        # Authenticating Employee
        u = authenticate(username=uname, password=psw)
        if u is not None:
            if e.department == "Business":
                # request.session['username'] = uname
                return redirect('home')
            elif e.department == "CS":
                request.session['username'] = uname
                return redirect('CSinterface')
            elif e.department == "Staff":
                request.session['username'] = uname
                return redirect('Staffinterface')
            elif e.department == "Manager":
                request.session['username'] = uname
                return redirect('managerinterface')
            else:
                return HttpResponse("Not a Valid user")
        else:
            return render(request, 'emplogin.html', {'message': 'Invalid Password. Please try again!!', 'user': ''})
    else:
        return render(request, 'emplogin.html', {'user': ''})


def Employee_logout(request):
    auth.logout(request)
    request.session.clear()
    return render(request, 'emplogout.html', {'user': ''})


# Customer Service Interface shows only pending loans from ML Verification
@cs_not_loggedin
def CSinterface(request):
    uid = request.session['username']
    u = User.objects.get(username=uid)
    bus = Business_Verification.objects.filter(ml_status="Accepted", mv_status="CS")
    # Interface for pending customers
    if request.method == "POST" and "view" in request.POST:
        loan_id = request.POST.get('view')
        cv = Customer_Verification.objects.filter(loan_id=loan_id, ml_status="Accepted", mv_status="CS")
        request.session['loan_id'] = loan_id
        return render(request, "Interfaces/csapproval.html", {'cust': cv})
    # Update customer's status
    elif request.method == "POST" and "updatecustomer" in request.POST:
        loan_id = request.session['loan_id']
        cid = request.POST.get('updatecustomer')
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")
        callstatus = request.POST.get("phonecallstatus")
        addr_status = request.POST.get("addressstatus")
        cv = Customer_Verification.objects.filter(loan_id=loan_id, ml_status="Accepted",mv_status='CS',c_id=cid)

        for i in cv:
            cus = Customer.objects.get(loan_id=loan_id, c_id=cid)
            bus = Business_Loan_Application.objects.get(loan_id=loan_id)
            if CustomerService_Details_Customer.objects.filter(loan_id=bus, c_id=cus).exists():
                csdetails = CustomerService_Details_Customer.objects.get(loan_id=bus, c_id=cus)
            else:
                csdetails = CustomerService_Details_Customer(loan_id=bus, c_id=cus)
            csdetails.c_owner_name = cus.c_owner_name
            csdetails.cb_name = cus.cb_name
            csdetails.cb_type = cus.cb_type
            csdetails.cb_invoice_amt = cus.cb_invoice_amt
            csdetails.cb_email = cus.cb_email
            csdetails.cb_contact = cus.cb_contact
            csdetails.cs_remarks = remarks
            csdetails.phonecall_status = callstatus
            csdetails.address_status = addr_status
            if status == "Accepted":
                csdetails.cs_status = 'Accepted'
                csdetails.save()
                i.mv_status = "LOA"
                i.mv_remarks = 'CS:' + str(remarks)
                i.save()

            else:
                csdetails.cs_status = 'Rejected'
                csdetails.save()
                i.mv_status = "Rejected in CS"
                i.mv_remarks = 'CS:' + str(remarks)
                i.final_status = "Rejected"
                i.save()
                bid = Business.objects.get(b_id=bus.b_id.b_id)
                sendemailcustomers(request, 2, bid, bus, cus)
                cv1 = Customer_Verification.objects.filter(loan_id=loan_id, ml_status="Accepted").count()
                cv2 = Customer_Verification.objects.filter(loan_id=loan_id, final_status="Rejected").count()
                if cv1 == cv2:
                    bv = Business_Verification.objects.get(loan_id=loan_id)
                    bv.final_status = "Rejected"
                    bv.mv_status = "All Customers rejected in CS"
                    bv.mv_remarks = "Rejected in CS"
                    bv.loa_status = "Not Yet Sent"
                    bv.save()
                    if bv.mv_reverify == 'Yes':
                        rl = Business_Loan_Application.objects.get(loan_id=bus.loan_id)
                        rl.b_status = 'Verification Rejected'
                        rl.loan_status = 'Inactive'
                        rl.save()
                        reject = Rejected_Loans()
                        reject.b_id = bid
                        reject.loan_id = rl
                        reject.status = 'Rejected'
                        reject.remarks = 'All Customers Rejected in CS Re-Verification'
                        reject.save()
                        sendemailbusiness(request, 5, bid.b_id, loan_id)
                    message = 'Loan Rejected due to all Customers Rejection'
                    bv = Business_Verification.objects.filter(ml_status="Accepted", mv_status="CS")
                    return render(request, "Interfaces/customerservice.html", {'bus': bv, 'message': message})
        cv = Customer_Verification.objects.filter(loan_id=loan_id, ml_status="Accepted", mv_status='CS')
        message = "Customer Status Updated Successfully!!"
        return render(request, "Interfaces/csapproval.html", {'cust': cv, 'message': message})
    # Update Business status
    elif request.method == "POST" and "updatebusiness" in request.POST:
        loan_id = request.session['loan_id']
        bstatus = request.POST.get('bstatus')
        remarks = request.POST.get('remarks')
        b_callstatus = request.POST.get("busphonecallstatus")
        b_addr_status = request.POST.get("busaddressstatus")
        bus = Business_Verification.objects.get(loan_id=loan_id, ml_status="Accepted", mv_status="CS")
        bid = Business.objects.get(b_id=bus.b_id.b_id)
        bl = Business_Loan_Application.objects.get(loan_id=loan_id)
        cv = Customer_Verification.objects.filter(loan_id=bl, b_id=bid, mv_status="LOA")

        if CustomerService_Details_Business.objects.filter(loan_id=bl).exists():
            b_csdetails = CustomerService_Details_Business.objects.get(loan_id=bl)
            b_csdetails.save()
        else:
            b_csdetails = CustomerService_Details_Business(loan_id=bl)
            b_csdetails.b_id = bid
            b_csdetails.b_email = bid.b_email
            b_csdetails.b_contact = bid.b_contact
            b_csdetails.phonecall_status = b_callstatus
            b_csdetails.address_status = b_addr_status
            b_csdetails.reverification = bus.mv_reverify
            b_csdetails.cs_status = bstatus
            b_csdetails.cs_remarks = remarks
            b_csdetails.save()

        if bstatus == "Accepted":
            bus.mv_status = "LOA for Customers"
            bus.loa_status = "Not Yet Sent"
            bus.mv_remarks = 'CS:' + str(remarks)
            # add business sanctioned amnt
            # bus.sanctioned_amount +=
            for i in range(len(cv)):
                cv[i].loa_status = "LOA Sent"
                cv[i].save()
            sendloacustomers(request, loan_id)
        else:
            bus.mv_status = "Rejected in CS"
            bus.mv_remarks = 'CS:' + str(remarks)
            bus.final_status = "Rejected"

            for i in range(len(cv)):
                cv[i].mv_status = 'Rejected due to Business'
                cv[i].final_status = 'Rejected'
                cv[i].loa_status = 'Not Applicable'
                cv[i].save()
                if bus.mv_reverify == 'Yes':
                    rl = Business_Loan_Application.objects.get(loan_id=loan_id)
                    rl.b_status = 'Verification Rejected'
                    rl.loan_status = 'Inactive'
                    rl.save()
                    reject = Rejected_Loans()
                    reject.b_id = bid
                    reject.loan_id = rl
                    reject.status = 'Rejected'
                    reject.remarks = 'Business Rejected in CS Re-Verification'
                    reject.save()
                    sendemailbusiness(request, 6, bid.b_id, loan_id)
        bus.save()
        message = 'Details have been Updated Successfully!'
        bus = Business_Verification.objects.filter(mv_status="CS")
        return render(request, "Interfaces/customerservice.html", {'bus': bus, 'message': message})
    else:
        return render(request, 'Interfaces/customerservice.html', {'user': u, 'bus': bus})


@staff_not_loggedin
def Staffinterface(request):
    bus = Business_Verification.objects.filter(mv_status="ST", final_status="Pending")
    if request.method == "POST" and "view" in request.POST:
        loan_id = request.POST.get('view')
        cv = Customer_Verification.objects.filter(loan_id=loan_id, ml_status="Accepted", mv_status='ST')
        request.session['count'] = cv.count()
        request.session['loan_id'] = loan_id
        return render(request, "Interfaces/stapproval.html", {'cust': cv})

    elif request.method == "POST" and "updatecustomer" in request.POST:
        loan_id = request.session['loan_id']
        cid = request.POST.get('updatecustomer')
        cv = Customer_Verification.objects.filter(c_id=cid, loan_id=loan_id, ml_status="Accepted", mv_status="ST")
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")

        # Taking customer files from staff
        boolval = request.FILES.get('c_file_audit', False)
        if boolval != False:
            file = request.FILES['c_file_audit']
            filename = 'st_file_audit'
            fs = FileSystemStorage()
            extension = str(file).split('.')
            st_audit_path = 'http://127.0.0.1:8000/media/' + fs.save('StaffFiles/'+str(loan_id)+'/'+str(cid)+'/'+str(filename)+'.'+extension[1], file)
        else:
            st_audit_path = 'None'

        boolval = request.FILES.get('c_sales_ledger', False)
        if boolval != False:
            file = request.FILES['c_sales_ledger']
            filename = 'st_sales_ledger'
            fs = FileSystemStorage()
            extension = str(file).split('.')
            st_ledger_path = 'http://127.0.0.1:8000/media/' + fs.save('StaffFiles/' + str(loan_id) + '/' + str(cid) + '/' + str(filename) + '.' + extension[1], file)
        else:
            st_ledger_path = 'None'

        boolval = request.FILES.get('c_file_invoice', False)
        if boolval != False:
            filename = 'st_file_invoice'
            file = request.FILES['c_file_invoice']
            extension = str(file).split('.')
            fs = FileSystemStorage()
            st_file_invoice_path = 'http://127.0.0.1:8000/media/' + fs.save('StaffFiles/' + str(loan_id) + '/' + str(cid) + '/' + str(filename) + '.' + extension[1], file)
        else:
            st_file_invoice_path = 'None'

        boolval = request.FILES.get('c_file_statement', False)
        if boolval != False:
            filename = 'st_file_statement'
            file = request.FILES['c_file_statement']
            fs = FileSystemStorage()
            extension = str(file).split('.')
            st_file_statement_path = 'http://127.0.0.1:8000/media/'+str(fs.save('StaffFiles/' + str(loan_id) + '/' + str(cid) + '/' + str(filename) + '.' + extension[1], file))
        else:
            st_file_statement_path = 'None'

        cus = Customer.objects.get(loan_id=loan_id, c_id=cid)
        bus = Business_Loan_Application.objects.get(loan_id=loan_id)
        if Staff_Details_Customer.objects.filter(loan_id=bus, c_id=cus).exists():
            staffdetails = Staff_Details_Customer.objects.get(loan_id=bus, c_id=cus)
        else:
            staffdetails = Staff_Details_Customer(loan_id=bus, c_id=cus)

        staffdetails.cb_invoice_amt = cus.cb_invoice_amt
        staffdetails.st_file_audit = st_audit_path
        staffdetails.st_sales_ledger = st_ledger_path
        staffdetails.st_file_invoice = st_file_invoice_path
        staffdetails.st_file_statement = st_file_statement_path
        staffdetails.save()
        for i in cv:
            if status == "Accepted":
                staffdetails.st_status = 'Accepted'
                i.mv_status = "M"
                i.mv_remarks = 'ST:' + str(remarks)
                i.save()
            else:
                staffdetails.st_status = 'Rejected'
                i.final_status = "Rejected"
                i.mv_status = "Rejected in ST"
                i.mv_remarks = 'ST:' + str(remarks)
                i.save()
                bid = Business.objects.get(b_id=bus.b_id.b_id)
                sendemailcustomers(request, 2, bid, bus, cus)
                # If all the customers get rejected then loan gets rejected
                count = request.session['count']
                cv1 = Customer_Verification.objects.filter(loan_id=loan_id).count()
                cv2 = Customer_Verification.objects.filter(loan_id=loan_id, final_status="Rejected").count()
                if cv2 == cv1:
                    bv = Business_Verification.objects.get(loan_id=loan_id)
                    bv.final_status = "Rejected"
                    bv.mv_status = "All Customers rejected in ST"
                    bv.mv_remarks = "Rejected in ST"
                    bv.save()
                    if bv.mv_reverify == 'Yes':
                        rl = Business_Loan_Application.objects.get(loan_id=loan_id)
                        rl.b_status = 'Verification Rejected'
                        rl.loan_status = 'Inactive'
                        rl.save()
                        reject = Rejected_Loans()
                        reject.b_id = bid
                        reject.loan_id = rl
                        reject.status = 'Rejected'
                        reject.remarks = 'All Customers Rejected in ST Re-Verification'
                        reject.save()
                    sendemailbusiness(request, 5, bid.b_id, loan_id)
                    bus = Business_Verification.objects.filter(mv_status="ST", final_status="Pending")
                    message = "Loan Rejected due to all Customers Rejection"
                    return render(request, "Interfaces/staffing.html", {'bus': bus, 'message': message})
        cv = Customer_Verification.objects.filter(loan_id=loan_id, ml_status="Accepted", mv_status="ST")
        return render(request, "Interfaces/stapproval.html", {'cust': cv, 'message': 'Customer Status Updated Successfully!!'})
    # Update Business status
    elif request.method == "POST" and "updatebusiness" in request.POST:
        loan_id = request.session['loan_id']
        bus = Business_Verification.objects.get(loan_id=loan_id, ml_status="Accepted", mv_status="ST")
        bstatus = request.POST.get('status')
        remarks = request.POST.get('remarks')

        # Taking files from staff
        boolval = request.FILES.get('b_file_audit', False)
        if boolval!=False:
            file = request.FILES['b_file_audit']
            filename = 'bus_st_file_audit'
            extension = str(file).split('.')
            fs = FileSystemStorage()
            bst_audit_path = 'http://127.0.0.1:8000/media/' + fs.save('StaffFiles/' + str(loan_id) + '/' + str(filename) + '.' + extension[1], file)
        else:
            bst_audit_path = 'None'

        boolval = request.FILES.get('b_sales_ledger', False)
        if boolval != False:
            file = request.FILES['b_sales_ledger']
            filename = 'bus_st_file_saleledger'
            extension = str(file).split('.')
            fs = FileSystemStorage()
            bst_ledger_path = 'http://127.0.0.1:8000/media/' + fs.save('StaffFiles/' + str(loan_id) + '/' + str(filename) + '.' + extension[1], file)
        else:
            bst_ledger_path = 'None'

        # Storing details  in Staff_Details_Business table
        loanid = Business_Loan_Application.objects.get(loan_id=loan_id)
        bid = Business.objects.get(b_id=loanid.b_id.b_id)
        if Staff_Details_Business.objects.filter(loan_id=loanid, b_id=bid).exists():
            staffdetails = Staff_Details_Business.objects.get(loan_id=loanid, b_id=bid)
        else:
            staffdetails = Staff_Details_Business(loan_id=loanid, b_id=bid)
        staffdetails.b_st_file_audit = bst_audit_path
        staffdetails.b_st_sales_ledger = bst_ledger_path
        if bstatus == 'Accepted':
            bus.mv_status = "M"
            bus.mv_remarks = 'ST:' + str(remarks)
            staffdetails.b_st_status = "Accepted"
            staffdetails.b_st_remarks = remarks
        else:
            bus.mv_status = "Rejected in ST"
            bus.mv_remarks = 'ST:' + str(remarks)
            bus.final_status = "Rejected"
            staffdetails.b_st_status = "Rejected"
            staffdetails.b_st_remarks = remarks
            cv = Customer_Verification.objects.filter(loan_id=loan_id, b_id=bid, mv_status='M')
            for i in range(len(cv)):
                cv[i].mv_status = 'Rejected due to Business'
                cv[i].final_status = 'Rejected'
                cv[i].save()
        # If a loan has been rejected in reverification then it is final reject
            if bus.mv_reverify == 'Yes':
                rl = Business_Loan_Application.objects.get(loan_id=loan_id)
                rl.b_status = 'Verification Rejected'
                rl.loan_status = 'Inactive'
                rl.save()
                reject = Rejected_Loans()
                reject.b_id = bid
                reject.loan_id = rl
                reject.status = 'Rejected'
                reject.remarks = 'Business Rejected in ST Re-Verification'
                reject.save()
                sendemailbusiness(request, 6, bid.b_id, loan_id)
        staffdetails.save()
        bus.save()
        message = 'Details have been Updated Successfully!'
        bus = Business_Verification.objects.filter(mv_status="ST")
        return render(request, "Interfaces/staffing.html", {'bus': bus, 'message': message})
    else:
        return render(request, "Interfaces/staffing.html", {'bus': bus})


@manager_not_loggedin
def managerinterface(request):
    if request.method == "POST" and "approved_loans" in request.POST:
        bus = Business_Verification.objects.filter(mv_status="M")
        return render(request, 'Interfaces/manager_interface_approved_loans.html', {'bus': bus})
    elif request.method == "POST" and "approvedcustomers" in request.POST:
        loan_id = request.POST.get('approvedcustomers')
        request.session['loan_id'] = loan_id
        cv = Customer_Verification.objects.filter(loan_id=loan_id, mv_status="M")
        ob1 = Staff_Details_Business.objects.get(loan_id=loan_id)
        return render(request, 'Interfaces/manager_interface_approved_customers.html', {'cust': cv, 'ob1': ob1})
    elif request.method == "POST" and "cdocs" in request.POST:
        loan_id = request.session['loan_id']
        cid = request.POST.get("cdocs")
        request.session['c_id'] = cid
        staff = Staff_Details_Customer.objects.filter(loan_id=loan_id, c_id=cid)
        return render(request, 'Interfaces/manager_interface_cdocs.html', {'staff': staff})
    elif request.method == "POST" and "updatebusiness" in request.POST:
        loan_id = request.session['loan_id']
        bv = Business_Verification.objects.get(loan_id=loan_id)
        bid = Business.objects.get(b_id=bv.b_id.b_id)
        bl = Business_Loan_Application.objects.get(b_id=bid, loan_id=loan_id)
        remarks = request.POST.get("remarks")
        m = Manager(loan_id=bl)
        if request.POST.get("status") == "Accepted":
            bv.mv_status = "Accepted in M"
            bv.mv_accuracy = decimal.Decimal(round(random.uniform(69, 90), 1))
            bv.mv_remarks = "M:"+str(remarks)
            sendemailbusiness(request, 3, bid.b_id, loan_id)
            bv.loa_status = 'LOA sent'
            bl.b_status = 'Verification Accepted'
            m.m_status = "Accepted"
            m.m_remarks = bv.mv_remarks
        else:
            bv.mv_status = "Rejected in M"
            bv.mv_accuracy = decimal.Decimal(round(random.uniform(40, 69), 1))
            bv.mv_remarks = "M:"+str(remarks)
            bv.final_status = "Rejected"
            bl.b_status = 'Verification Rejected'
            bl.loan_status = 'Inactive'
            m.m_status = "Rejected"
            m.m_remarks = bv.mv_remarks
            reject = Rejected_Loans()
            reject.b_id = bid
            reject.loan_id = bl
            reject.status = 'Rejected'
            reject.remarks = 'Business Rejected by Manager'
            reject.save()
            sendemailbusiness(request, 6, bid.b_id, loan_id)
        m.save()
        bl.save()
        bv.save()
        message = "Details updated successfully"
        return render(request, 'Interfaces/manager_interface_approved_loans.html', {'message': message})

    elif request.method == "POST" and "updatecustomer" in request.POST:
        loan_id = request.session['loan_id']
        bl = Business_Loan_Application.objects.get(loan_id=loan_id)
        b = Business.objects.get(b_id=bl.b_id.b_id)
        cid = request.POST.get("updatecustomer")
        cv = Customer_Verification.objects.get(loan_id=loan_id, c_id=cid)
        remarks = request.POST.get("remarks")
        if request.POST.get("status") == "Accepted":
            cv.mv_status = "Accepted in M"
            cv.mv_remarks = "M:" + str(remarks)
            cv.save()
        else:
            cv.mv_status = "Rejected in M"
            cv.mv_remarks = "M:" + str(remarks)
            cv.final_status = "Rejected"
            cv.save()
            # sendemailcustomers(request, 2, b, bl, cus)
        cv1 = Customer_Verification.objects.filter(loan_id=loan_id).count()
        cv2 = Customer_Verification.objects.filter(loan_id=loan_id, final_status="Rejected").count()
        if cv1 == cv2:
            bv1 = Business_Verification.objects.get(loan_id=loan_id)
            bv1.mv_status = "Rejected in M"
            bv1.mv_remarks = "M:" + str(remarks)
            bv1.final_status = "Rejected"
            bv1.loa_status = "Not Yet Sent"
            bv1.save()
            reject = Rejected_Loans()
            reject.b_id = b
            reject.loan_id = bl
            reject.status = 'Rejected'
            reject.remarks = 'All Customers Rejected by Manager'
            reject.save()
            m = Manager(loan_id=bl, m_status='Rejected', remarks=remarks)
            m.save()
            bl.b_status = "Verification Rejected"
            bl.loan_status = "Inactive"
            bl.save()
            bid = Business.objects.get(b_id=bv1.b_id.b_id)
            sendemailbusiness(request, 6, bid.b_id, loan_id)
            message = "Loan has been Rejected because all customers are Rejected"
            return render(request, 'Interfaces/manager_interface_approved_loans.html', {'message': message})

        cv = Customer_Verification.objects.filter(loan_id=loan_id, mv_status="M")
        ob1 = Staff_Details_Business.objects.get(loan_id=loan_id)
        message = 'Customer Status updated Successfully!!'
        return render(request, 'Interfaces/manager_interface_approved_customers.html', {'cust': cv, 'ob1': ob1, 'message': message})

    elif request.method == "POST" and "rejected_loans" in request.POST:
        reject = Business_Verification.objects.filter(final_status="Rejected", loa_status='Not Yet Sent', mv_reverify='No').exclude(mv_status__in=['Rejected due to customers LOA', 'Rejected in M'])
        return render(request, 'Interfaces/manager_interface_rejected_loans.html', {'reject': reject})
    elif request.method == "POST" and "view_details" in request.POST:
        loan_id = request.POST.get('view_details')
        request.session['loan_id'] = loan_id
        cust = Customer_Verification.objects.filter(loan_id=loan_id)
        bus = Business_Verification.objects.get(loan_id=loan_id)
        return render(request, "Interfaces/manager_interface_rejected_customers.html", {'cust': cust, 'bus': bus})
    elif request.method == "POST" and "sendtoCS" in request.POST:
        loan_id = request.session['loan_id']
        bl = Business_Loan_Application.objects.get(loan_id=loan_id)
        cv = Customer_Verification.objects.filter(loan_id=loan_id)
        bv = Business_Verification.objects.get(loan_id=loan_id)
        remarks = request.POST.get("remarks")
        for i in cv:
            i.mv_status = "CS"
            i.mv_remarks = "Sent from Manager"
            i.loa_status = "Not Yet Sent"
            i.mv_reverify = "Yes"
            i.final_status = "Pending"
            i.save()
        bv.mv_status = "CS"
        bv.mv_remarks = 'M:' + remarks
        bv.loa_status = "Not Yet Sent"
        bv.mv_reverify = "Yes"
        bv.final_status = "Pending"
        bv.save()
        bl.b_status = "Under Business verification"
        bl.loan_status = "Active"
        bl.save()
        m = Manager(loan_id=bl, m_status='Rejected', reverify="Yes", remarks='Reverify')
        m.save()
        message = "Details sent to CS successfully"
        return render(request, 'Interfaces/managerinterface.html', {'message': message})
    elif request.method == "POST" and "reject" in request.POST:
        loan_id = request.session['loan_id']
        bl = Business_Loan_Application.objects.get(loan_id=loan_id)
        bid = Business.objects.get(b_id=bl.b_id.b_id)
        cv = Customer_Verification.objects.filter(loan_id=loan_id)
        bv = Business_Verification.objects.get(loan_id=loan_id)
        remarks = request.POST.get("remarks")
        bl.loan_status = "Inactive"
        bl.b_status = "Verification Rejected"
        bv.mv_status = "Rejected in M"
        bv.mv_remarks = remarks
        bv.final_status = "Rejected"
        bl.save()
        bv.save()
        reject = Rejected_Loans()
        reject.b_id = bid
        reject.loan_id = bl
        reject.status = 'Rejected'
        reject.remarks = 'Business Rejected in Manual Verification'
        reject.save()
        sendemailbusiness(request, 6, bid.b_id, loan_id)
        for customer in cv:
            customer.mv_status = "Rejected in M"
            customer.final_status = "Rejected"
            customer.save()
        message = "Loan Status Updated Successfully"
        reject = Business_Verification.objects.filter(final_status="Rejected", loa_status='Not Yet Sent',mv_reverify='No').exclude(mv_status__in=['Rejected due to customers LOA', 'Rejected in M'])
        return render(request, 'Interfaces/manager_interface_rejected_loans.html', {'reject': reject, 'message': message})
    else:
        return render(request, "Interfaces/managerinterface.html")

# Investor Registration form details
def investor_register(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        uvalid = User.objects.filter(username=username).exists()
        if not uvalid:
            investor_phone_number = request.POST.get('phone')
            investment_amount = request.POST.get('investment_amount')
            email = request.POST.get('email')
            u = User(username=username)
            u.set_password(request.POST.get('password'))
            u.email = email
            u.save()
            emp = UTEmployees()
            emp.user = u
            emp.department = "Investor"
            emp.save()

            if Mapping_values.objects.count() == 0:
                Mapping_values(investor_map_value=1).save()

            inv = Investor(investor_id='investor_'+str(Investor.objects.count()+1))
            inv.inv_user = username
            inv.investor_mail_id = email
            inv.investor_phone_number = investor_phone_number
            inv.investment_amount = investment_amount
            inv.available_amount = investment_amount
            inv.save()
            request.session['uname'] = username
            return redirect('investor_interface')
        else:
            message = 'Username already exists/Not available username'
            return render(request, 'Interfaces/investor_register.html', {'message': message})
    else:
        return render(request, 'Interfaces/investor_register.html', {'user': ''})

# Investor Login Authentication
def investor_login(request):
    if request.method == "POST":
        uname = request.POST.get("uname")
        try:
            uid = User.objects.get(username=uname)
        except User.DoesNotExist:
            return render(request, 'Interfaces/investor_login.html', {'message': 'Investor with that Credentials does not exists!!', 'user': ''})
        psw = request.POST.get("password")
        # Authenticating Investor
        u = authenticate(username=uname, password=psw)
        if u is not None:
            request.session['uname'] = uname
            ut = UTEmployees.objects.get(user=uid)
            if ut.department == 'Investor':
                return redirect('investor_interface')
        else:
            return render(request, 'Interfaces/investor_login.html', {'message': 'Invalid Credentials, Please try again with valid details', 'user': ''})
    else:
        return render(request, 'Interfaces/investor_login.html', {'user': ''})

@investor_not_loggedin
def investor_interface(request):
    username = request.session['uname']
    user=User.objects.get(username=username)
    if Investor.objects.filter(inv_user=user).exists():
        investor = Investor.objects.get(inv_user=user)
        return render(request, 'Interfaces/investor_interface.html', {'ob1': investor, 'user': username})
    else:
        return redirect('investor_login')

def investor_logout(request):
    auth.logout(request)
    request.session.clear()
    return render(request, 'Interfaces/investor_login.html', {'message': 'Loggedout succesfully', 'user': ''})


# Storing details of Business which are accepted in Verification
def accepted_business(request, bid, loan_id):
    bv = Business_Verification.objects.get(final_status='Accepted', loan_id=loan_id)
    bl = Business_Loan_Application.objects.get(loan_id=loan_id)
    bid = Business.objects.get(b_id=bl.b_id.b_id)
    st_bus = Staff_Details_Business.objects.get(loan_id=loan_id, b_id=bid.b_id)
    cs_bus = CustomerService_Details_Business.objects.get(loan_id=loan_id, b_id=bid.b_id)
    req_amount = bv.requested_amount
    customers = Customer_Verification.objects.filter(final_status='Accepted', loan_id=bl)
    sanct_amount = 0
    for i in customers:
            cus = Customer.objects.get(c_id=i.c_id.c_id)
            cs_cus = CustomerService_Details_Customer.objects.get(c_id=i.c_id, loan_id=loan_id)
            st_cus = Staff_Details_Customer.objects.get(c_id=i.c_id, loan_id=loan_id)
            if Accepted_Customers.objects.filter(c_id=cus, loan_id=bl).exists():
                data = Accepted_Customers.objects.get(c_id=cus)
                data.delete()
            data = Accepted_Customers()
            data.c_id = cus
            data.loan_id = bl
            data.b_id = bid
            data.invoice_amount = cus.cb_invoice_amt
            data.due_date = cus.c_due_date
            data.c_owner_name = cus.c_owner_name
            data.cb_name = cus.cb_name
            data.cb_contact = cus.cb_contact
            data.cb_email = cus.cb_email
            data.cb_address = cus.cb_address
            data.cb_type = cus.cb_type
            data.cb_relation = cus.cb_relation
            data.cb_pan_no = cus.cb_pan_no
            data.cb_est_date = cus.cb_est_date
            data.cb_turnover = cus.cb_turnover
            data.cb_invoice_no = cus.cb_invoice_no
            data.cb_invoice_amt = cus.cb_invoice_amt
            data.c_issue_date = cus.c_issue_date
            data.c_due_date = cus.c_due_date
            data.c_file_audit = cus.c_file_audit
            data.c_sales_ledger = cus.c_sales_ledger
            data.c_file_invoice = cus.c_file_invoice
            data.c_file_statement = cus.c_file_statement
            data.ml_accuracy = i.ml_accuracy
            data.ml_status = i.ml_status
            data.ml_remarks = i.ml_remarks
            data.mv_accuracy = i.mv_accuracy
            data.mv_status = i.mv_status
            data.mv_remarks = i.mv_remarks
            data.mv_reverify = i.mv_reverify
            data.final_status = i.final_status
            data.loa_status = i.loa_status
            data.phonecall_status = cs_cus.phonecall_status
            data.address_status = cs_cus.address_status
            data.cs_remarks = cs_cus.cs_remarks
            data.st_file_audit = st_cus.st_file_audit
            data.st_sales_ledger = st_cus.st_sales_ledger
            data.st_file_invoice = st_cus.st_file_invoice
            data.st_file_statement = st_cus.st_file_statement
            data.st_remarks = st_cus.st_remarks
            data.pay_link = 'NA'
            data.save()
            sanct_amount += data.invoice_amount

    if Accepted_Business.objects.filter(loan_id=loan_id).exists():
        ab = Accepted_Business.objects.get(loan_id=loan_id)
        ab.b_id = bid
        ab.requested_amount = req_amount
        ab.sanctioned_amount = sanct_amount
    else:
        ab = Accepted_Business(b_id=bid, requested_amount=req_amount, loan_id=bl, sanctioned_amount=sanct_amount)
    ab.b_name = bid.b_name
    ab.b_owner_name = bid.b_owner_name
    ab.b_email = bid.b_email
    ab.b_contact = bid.b_contact
    ab.b_addr = bid.b_addr
    ab.b_pan_no = bid.b_pan_no
    ab.b_est_date = bid.b_est_date
    ab.b_type = bid.b_type
    ab.b_applied_date = bid.b_applied_date
    ab.adv_details = bid.adv_details
    ab.b_turnover = bl.b_turnover
    ab.b_required_loan_amount = bl.b_total_invoice_amount
    ab.b_no_of_invoices = bl.b_no_of_invoices
    ab.b_audit_path = bl.b_audit_path
    ab.b_ledger_path = bl.b_ledger_path
    ab.b_status = bl.b_status
    ab.loan_status = bl.loan_status
    ab.applied_date = bl.applied_date
    ab.b_reason_to_apply = bl.b_reason_to_apply
    ab.b_st_file_audit = st_bus.b_st_file_audit
    ab.b_st_sales_ledger = st_bus.b_st_sales_ledger
    ab.b_st_status = st_bus.b_st_status
    ab.b_st_remarks = st_bus.b_st_remarks
    ab.ml_accuracy = bv.ml_accuracy
    ab.ml_status = bv.ml_status
    ab.ml_remarks = bv.ml_remarks
    ab.mv_accuracy = bv.mv_accuracy
    ab.mv_status = bv.mv_status
    ab.mv_remarks = bv.mv_remarks
    ab.mv_reverify = bv.mv_reverify
    ab.final_status = bv.final_status
    ab.requested_amount = bv.requested_amount
    ab.loa_status = bv.loa_status
    ab.sanctioned_amount = sanct_amount

    bv.sanctioned_amount = sanct_amount
    # bl.sanctioned_amount = sanct_amount
    bv.save()
    ab.save()
    mapInvestor(ab, loan_id)
    disburse(request, bl)


# Mapping Business loan to Investor
def mapInvestor(data, loan_id):
    value = False
    currentInvestor = Mapping_values.objects.get()
    investorMapValue = currentInvestor.investor_map_value
    investor_id = "investor_"+str(investorMapValue)
    check = Investor.objects.filter(investor_id=investor_id).exists()
    if check == True:
        inv = Investor.objects.get(investor_id=investor_id)
        total_number_investors = Investor.objects.count()
        amount = data.sanctioned_amount*80/100
        if inv.available_amount >= amount:
            inv.available_amount = inv.available_amount-amount
            inv.disbursement_amount = decimal.Decimal(inv.disbursement_amount)+amount
            inv.save()
            if Investor_mapping.objects.filter(loan_id=Business_Loan_Application.objects.get(loan_id=loan_id)).exists():
                investorMapping = Investor_mapping.objects.get(loan_id=Business_Loan_Application.objects.get(loan_id=loan_id))
            else:
                investorMapping = Investor_mapping()
            investorMapping.investor_id = inv
            investorMapping.loan_id = Business_Loan_Application.objects.get(loan_id=loan_id)
            investorMapping.amount = amount
            investorMapping.disbursement_date = datetime.now()
            investorMapping.save()
            investorMapValue = (investorMapValue%total_number_investors)+1
            currentInvestor.investor_map_value = investorMapValue
            currentInvestor.save()
        else:
            investorMapValue = (investorMapValue%total_number_investors)+1
            currentInvestor.investor_map_value = investorMapValue
            currentInvestor.save()
            mapInvestor(data, loan_id)
    else:
        print('Investor not available')


# ---- Business Loan Disbursement-----
def disburse(request, loan_id):
    b_data = Accepted_Business.objects.get(loan_id=loan_id)
    sanction_amount = b_data.sanctioned_amount
    disburseamount = sanction_amount*80/100
    remaining_amount = sanction_amount*10/100
    vpa = get_random_string(length=10) + str(loan_id.loan_id)
    data = Disbursement(loan_id=loan_id, b_id=b_data.b_id, disburse_amount=disburseamount, vpa=vpa, status='First Disbursement')
    data.save()
    b_data.one_disburse_amount = disburseamount
    b_data.one_disburse_date = datetime.now()
    b_data.one_disburse_id = data.disburse_id
    b_data.two_disburse_amount = remaining_amount
    b_data.satus = "First disbursement done"
    b_data.save()
    loan_id.b_status = 'Disbursment done'
    loan_id.save()
    customers = Accepted_Customers.objects.filter(loan_id=loan_id)
    for customer in customers:
        cus = Customer.objects.get(c_id=customer.c_id.c_id)
        link = Cus_virtualpayment(request, b_data.b_id, loan_id, cus)
        customer.status = "Not Paid"
        customer.pay_link = link
        customer.save()


# Creating virtual Payment link for customer Invoice Repayment
def Cus_virtualpayment(request, b_id, loan_id, c_id):
    vpa = get_random_string(length=10) + str(loan_id.loan_id) + str(c_id.c_id)
    bl = Business_Loan_Application.objects.get(loan_id=loan_id.loan_id)
    cust = Accepted_Customers.objects.get(loan_id=bl, c_id=c_id)
    C_id = Customer.objects.get(loan_id=bl, c_id=c_id.c_id)
    details = VirtualPayment(loan_id=bl, vpa=vpa, b_id=b_id, c_id=c_id, expiry_date=cust.due_date + timedelta(days=20),
                             amount=cust.invoice_amount)
    details.save()
    link = repaymentmail(request, b_id, loan_id, c_id, vpa)
    return link

# Sending repayment link to customer's Email Id
def repaymentmail(request, b_id, loan_id, cust, vpa):
    ac_cust = Accepted_Customers.objects.get(c_id=cust, loan_id=loan_id)
    toaddress = [cust.cb_email]
    link = "http://127.0.0.1:8000/repayment/"+str(vpa)+"/"+str(loan_id.loan_id)+"/"+str(cust.c_id)
    ac_cust.pay_link = link
    ac_cust.save()
    text = "Hi! " + cust.c_owner_name + "<br/>I Hope you are doing well <br/>Here is the link for paying your Invoice due amount. Kindly do it before the due date <br/>"+' <a href="'+str(ac_cust.pay_link)+'" target=_blank> Click here to Pay</a>'
    subject = 'IBL Invoice Payment'
    msg = EmailMessage(subject, text, '', toaddress)
    msg.content_subtype = "html"
    msg.send()
    return link

# Customer's response page for payment and storing payment details
def repayment(request, vpa, loan_id, c_id):
    if request.method == 'POST' and 'submit' in request.POST:
        acceptedCustomer = Accepted_Customers.objects.get(loan_id=loan_id, c_id=c_id)
        repaid_date = acceptedCustomer.due_date
        no_days = (datetime.now().date()-repaid_date).days
        if no_days <= 0:
            acceptedCustomer.repaid_date = datetime.now().date()
            acceptedCustomer.repaid_amount = acceptedCustomer.invoice_amount
            acceptedCustomer.status = "Paid"
        elif no_days < 21:
            interest = no_days*(acceptedCustomer.invoice_amount*1/100)
            total_amount = acceptedCustomer.invoice_amount+interest
            acceptedCustomer.repaid_date = datetime.now().date()
            acceptedCustomer.repaid_amount = total_amount
            acceptedCustomer.status = "Paid"
        acceptedCustomer.save()
        # Checking if all Customers have done the payment
        customerPayments = True
        customers = Accepted_Customers.objects.filter(loan_id=loan_id)
        for customer in customers:
            if customer.status != "Paid":
                customerPayments = False
        if customerPayments == True:
            bl = Business_Loan_Application.objects.get(loan_id=loan_id)
            bl.b_status = 'Repayment done'
            bl.save()
            time.sleep(30)
            # Second Disbursement for business
            acceptedBussiness = Accepted_Business.objects.get(loan_id=loan_id)
            acceptedBussiness.status = "Second Disbursement Done"
            bid = Business.objects.get(b_id=bl.b_id.b_id)
            disbursement = Disbursement()
            disbursement.b_id = bid
            disbursement.loan_id = bl
            disbursement.disburse_amount = acceptedBussiness.two_disburse_amount
            vpa = get_random_string(length=10) + str(bl.loan_id)
            disbursement.vpa = vpa
            disbursement.status = "Second Disbursement Done"
            disbursement.save()
            # Saving Second disbursement Id to accepted_business table
            acceptedBussiness.two_disburse_date = datetime.now()
            acceptedBussiness.two_disburse_id = disbursement.disburse_id
            acceptedBussiness.save()
            # Adding loan Changes to mapped Investor
            investorMap = Investor_mapping.objects.get(loan_id=loan_id)
            investor_id = investorMap.investor_id
            currentInvestor = Investor.objects.get(investor_id=investor_id.investor_id)
            currentInvestor.disbursement_amount = currentInvestor.disbursement_amount-acceptedBussiness.one_disburse_amount
            currentInvestor.available_amount = currentInvestor.available_amount + acceptedBussiness.one_disburse_amount
            currentInvestor.save()
            # Calculating total Profit after Interest on a loan
            interest_received = 0
            total_recieved = 0
            for customer in customers:
                interest_received = interest_received+(customer.repaid_amount-customer.invoice_amount)
                total_recieved += customer.repaid_amount
            profit_amount = total_recieved-acceptedBussiness.one_disburse_amount-acceptedBussiness.two_disburse_amount
            loan = Business_Loan_Application.objects.get(loan_id=loan_id)
            # Adding Interest to UTEarnings table
            UT_Earnings(investor_id=investor_id, b_id=acceptedBussiness, loan_id=loan, profit_amount=(profit_amount*90/100)).save()
            # Adding profit to mapped Investor
            currentInvestor.investor_profit += (profit_amount*10/100)
            currentInvestor.available_amount = currentInvestor.available_amount +(profit_amount*10/100)
            investorMap.status = 'Completed'
            investorMap.investor_profit = profit_amount*10/100
            acceptedBussiness.save()
            acceptedCustomer.save()
            currentInvestor.save()
            investorMap.save()
            # Changing loan status in Business_Loan_Application table
            bl.b_status = 'Second Disbursement done'
            bl.save()
            time.sleep(30)
            bl.b_status = 'Loan done'
            bl.loan_status = "Inactive"
            bl.final_status = 'Loan completed'
            bl.save()
            sendemailbusiness(request, 8, bl.b_id.b_id, loan_id)
            return HttpResponse("Your Payment is done!")
        else:
            return HttpResponse("Your Payment is Successful!!")
            # return HttpResponse("payment Error !")

    else:
        acceptedCustomer = Accepted_Customers.objects.get(loan_id=loan_id, c_id=c_id)
        if acceptedCustomer.repaid_amount != 0:
            return HttpResponse('You have already made the payment!!')
        due_date = acceptedCustomer.due_date
        no_days = (datetime.now().date()-due_date).days
        if no_days < 0:
            interest = 0
        elif no_days < 21:
            interest = no_days*(acceptedCustomer.invoice_amount*1/100)
        # elif no_days>15:
        #     return HttpResponse("Your Due date is expired. Contact your Business")
        else:
            return HttpResponse("Your Due date for Invoice Repayment has expired.Please Contact UT office")
        total_amount = acceptedCustomer.invoice_amount+interest
        return render(request, 'Repayment/repaymentmail.html', {'acceptedCustomer': acceptedCustomer, 'total_amount': total_amount})


def rejected_loans(request):
    bv = Business_Verification.objects.get(final_status="Rejected")
    reject = Rejected_Loans()
    reject.b_id = bv.b_id
    reject.loan_id = bv
    reject.status = bv.mv_status
    reject.remarks = bv.mv_remarks
    reject.save()
