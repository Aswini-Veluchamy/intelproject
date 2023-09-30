from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
# Create your views here.

@csrf_exempt
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        return HttpResponseRedirect('index')
    else:
        return render(request, "intel_app/login.html")

def user_logout(request):
    logout(request)
    try:
        del request.session["user_group"]
    except:
        pass
    return HttpResponseRedirect(reverse('login'))

def forgot_password(request):
    return render(request, 'intel_app/forgot_password.html')

def index(request):
    return render(request, 'intel_app/index.html')
