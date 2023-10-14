from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
import time
from .models import KeyMessage, KeyMessageTable, RiskTable
from .forms import PostForm

from .config import DEFAULT_PASSWORDS


@csrf_exempt
def user_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # Validating credentials with the database
        user = authenticate(request, username=username, password=password)
        if user:
            if password in DEFAULT_PASSWORDS:
                '''
                    if user password matches with default passwords
                    render the user to password management page
                '''
                return HttpResponseRedirect(reverse("home"))

            if list(user.groups.all()):
                '''
                    if user not tagged to the any project render error message to UI
                    else render to the respective home page 
                '''
                project = list(user.groups.all().values_list('name', flat=True))
            else:
                context['error'] = f"Please tag the project : {username}"
                return render(request, "intel_app/login.html", context)

            # redirecting to home screen
            login(request, user)
            request.session['meta_data'] = {'user_id': username, 'project': project}
            return HttpResponseRedirect(reverse("home"))
        else:
            context['error'] = "provide valid credentials"
            return render(request, "intel_app/login.html", context)
    else:
        return render(request, "intel_app/login.html")


def user_logout(request):
    logout(request)
    try:
        del request.session['meta_data']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('login'))


def forgot_password(request):
    return render(request, 'intel_app/forgot_password.html')


def home(request):
    return render(request, 'intel_app/index.html')


@csrf_exempt
def key_message(request):
    if request.method == "POST":
        message = request.POST['hiddenInput']
        project = request.POST['project']
        ''' storing data into database'''
        request_id = project[0:3] + "_" + str(int(time.time() * 1000))
        key_message_table = KeyMessageTable.objects.create(
            request_id=request_id,
            message=message,
            project=project,
            user=request.session['meta_data'].get('user_id')
        )
        key_message_table.save()
        return HttpResponseRedirect(reverse("key_message"))
    else:
        project = request.session['meta_data'].get('project')
        key_mess_data = KeyMessageTable.objects.all()
        return render(request, 'intel_app/key_message.html', {'data': key_mess_data, 'project': project})


@csrf_exempt
def key_message_test(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("key_message_test"))
    else:
        form = PostForm()
        post_view = KeyMessage.objects.all()
        return render(request, 'intel_app/key_message_test.html', {'post': post_view, 'form': form})


def post_list(request):
    post_view = KeyMessage.objects.all()
    return render(request, 'intel_app/post_list.html', {'post': post_view})


@csrf_exempt
def risk(request):
    if request.method == "POST":
        problem_statement = request.POST['problem_statement']
        status = request.POST['status']
        owner = request.POST['owner']
        message = request.POST['message']
        eta = request.POST['eta']
        risk = request.POST['risk']
        severity = request.POST['severity']
        impact = request.POST['impact']
        ''' storing data into database'''
        risk_data = RiskTable.objects.create(
            problem_statement=problem_statement,
            status=status,
            owner=owner,
            message=message,
            eta=eta,
            risk=risk,
            severity=severity,
            impact=impact
        )
        risk_data.save()
        return HttpResponseRedirect(reverse("risk"))
    else:
        risk_data = RiskTable.objects.all()
        return render(request, 'intel_app/risk_table.html', {'data': risk_data})

@csrf_exempt
def key_edit_message(request,pk):
    return render(request, 'intel_app/key_edit_message.html')