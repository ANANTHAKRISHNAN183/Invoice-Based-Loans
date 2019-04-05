from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, timezone, time
from firstapp.models import Accepted_Customers, Business_Loan_Application, Accepted_Business, Customer, Business, Collection, BlackListed
from django.core.mail import EmailMessage

class Command(BaseCommand):
    # @background(endswith=)
    def handle(self, *args, **kwargs):
        #s = sched.scheduler(time.time, time.sleep)
        datenow = datetime.now()
        duecustomers = Accepted_Customers.objects.filter(status='Not Paid')
        for ac_customer in duecustomers:
            no_days = (datenow.date() - ac_customer.due_date).days
            customer = Customer.objects.get(c_id=ac_customer.c_id.c_id)
            B_L = Business_Loan_Application.objects.get(loan_id=ac_customer.loan_id.loan_id)
            business = Business.objects.get(b_id=B_L.b_id.b_id)
            ac_business = Accepted_Business.objects.get(loan_id=B_L)
            if no_days > 0 and no_days < 16:
                toaddress = [customer.cb_email]
                text = "Hi! " + customer.c_owner_name + "<br/> I Hope you are doing well <br/> Here is the link for paying your Invoice due amount. As you have crossed the Invoice Due date, you need to pay additional Interest. Kindly do it before the due date.<br/> "+' <a href="'+str(ac_customer.pay_link)+'" target=_blank> Click here to pay</a>'
                subject = 'IBL INVOICE PAYMENT'
                msg = EmailMessage(subject, text, '', toaddress)
                msg.content_subtype = "html"
                msg.send()
                print('automatic Customer mail service done')
            elif no_days > 15 and no_days < 21:
                toaddress = [business.b_email]
                text = "Hi! your Customer with name :" + customer.c_owner_name + " Did not pay the Invoice Amount.<br/>So, As specified in the Agreement you need to pay that amount. Here is the link to pay Invoice due amount. Kindly do it before the  due date:"+str(ac_customer.due_date+timedelta(20))+" <br/> " + ' <a href="' + str(
                    ac_customer.pay_link) + '" target=_blank> Click here To PAY</a>'
                subject = 'IBL INVOICE PAYMENT'
                msg = EmailMessage(subject, text, '', toaddress)
                msg.content_subtype = "html"
                msg.send()
                print('automatic Business mail service done')
            elif no_days > 20:
                ac_customer.status = 'Collection'
                B_L.b_status = 'Collection'
                ac_business.status = 'Collection'
                if Collection.objects.filter(c_id=customer.c_id,loan_id=B_L.loan_id).exists():
                    collection=Collection.objects.get(c_id=customer.c_id,loan_id=B_L.loan_id)
                else:
                    collection = Collection()
                interest = no_days * (ac_customer.invoice_amount * 1 / 100)
                total_amount = ac_customer.invoice_amount + interest
                collection.c_id = customer
                collection.loan_id = B_L
                collection.b_id = business
                collection.invoice_amount = ac_customer.invoice_amount
                collection.repayment_amount = total_amount
                collection.due_date = ac_customer.due_date
                collection.save()
                ac_customer.save()
                ac_business.save()
                B_L.save()
                if no_days > 25:
                    if not BlackListed.objects.filter(b_pan_no=business.b_pan_no).exists():
                        blacklisted = BlackListed(b_pan_no=business.b_pan_no)
                        blacklisted.save()
                        print('Business has been added to blacklist as it reached ' + str(no_days) + ' days')
                print('Sending Customer to Collecton team ')
            else:
                print('automatic mail service done but no customers')