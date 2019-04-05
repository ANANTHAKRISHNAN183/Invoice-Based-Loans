from .models import User, UTEmployees
from django.shortcuts import render, redirect, HttpResponse


def cs_not_loggedin(function):
    def wrap(request, *args, **kwargs):
        # if User.is_active:
        #     auth.logout(request)
        #     request.session.clear()
        #     return redirect('employeelogin')
            # return redirect('logout')
        if not request.session.values():
            return redirect('employeelogin')
        elif request.session.values():
            uid = User.objects.get(username=request.session['username'])
            e = UTEmployees.objects.get(user=uid)
            if e.department == "CS":
                return function(request, *args, **kwargs)
            elif e.department == "Staff":
                return redirect('Staffinterface')
            elif e.department == "Manager":
                return redirect('managerinterface')
            else:
                return HttpResponse("Invalid employee")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def staff_not_loggedin(function):
    def wrap(request, *args, **kwargs):
        # vuid = User.objects.get(username=request.session['username'])
        # e = Employee.objects.get(user = vuid)
        if not request.session.values():
            return redirect('employeelogin')
        elif request.session.values():
            uid = User.objects.get(username=request.session['username'])
            e = UTEmployees.objects.get(user=uid)
            if e.department == "Staff":
                return function(request, *args, **kwargs)
            elif e.department == "CS":
                return redirect('CSinterface')
            elif e.department == "Manager":
                return redirect('managerinterface')
            elif e.department == "Investor":
                return redirect('investor_interface')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def manager_not_loggedin(function):
    def wrap(request, *args, **kwargs):
        # vuid = User.objects.get(username=request.session['username'])
        # e = Employee.objects.get(user = vuid)

        if not request.session.values():
            return redirect('employeelogin')
        elif request.session.values():
            uid = User.objects.get(username=request.session['username'])
            e = UTEmployees.objects.get(user=uid)
            if e.department == "Manager":
                return function(request, *args, **kwargs)
            elif e.department == "CS":
                return redirect('CSinterface')
            elif e.department == "Staff":
                return redirect('Staffinterface')
            elif e.department == "Investor":
                return redirect('investor_interface')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_not_loggedin(function):
    def wrap(request, *args, **kwargs):
        if not request.session.values():
            return redirect('login')
        elif request.session.values():
            uid = User.objects.get(username=request.session['uname'])
            e = UTEmployees.objects.get(user=uid)
            if e.department == "Business":
                return function(request, *args, **kwargs)
            # elif e.department == "Investor":
            #     return redirect('investor_interface')
            # elif e.department == "Manager":
            #     return redirect('managerinterface')
            # elif e.department == "CS":
            #     return redirect('CSinterface')
            # elif e.department == "Staff":
            #     return redirect('Staffinterface')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def investor_not_loggedin(function):
    def wrap(request, *args, **kwargs):
        if not request.session.values():
            return redirect('investor_login')
        elif request.session.values():
            uid = User.objects.get(username=request.session['uname'])
            e = UTEmployees.objects.get(user=uid)
            if e.department == "Investor":
                return function(request, *args, **kwargs)
            # elif e.department == "Manager":
            #     return redirect('managerinterface')
            # elif e.department == "CS":
            #     return redirect('CSinterface')
            # elif e.department == "Staff":
            #     return redirect('Staffinterface')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
