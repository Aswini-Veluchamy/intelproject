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

from .db_connection import load_key_message_data
from .db_connection import update_key_message_data
from .db_connection import load_risk_data
from .db_connection import update_risk_data


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
        user = request.session['meta_data'].get('user_id')
        message_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        key_message_table = KeyMessageTable.objects.create(
            message_id=message_id,
            message=message,
            project=project,
            user=request.session['meta_data'].get('user_id')
        )
        key_message_table.save()
        # load key message to external database
        load_key_message_data([(message_id, user, message, project)])
        return HttpResponseRedirect(reverse("key_message"))
    else:
        project = request.session['meta_data'].get('project')
        key_mess_data = KeyMessageTable.objects.filter(project__in=project)
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
def risks(request):
    if request.method == "POST":
        problem_statement = request.POST['problem_statement']
        status = request.POST['status']
        owner = request.POST['owner']
        message = request.POST['message']
        eta = request.POST['eta']
        risk = request.POST['risk']
        severity = request.POST['severity']
        impact = request.POST['impact']
        project = request.POST['project']

        user = request.session['meta_data'].get('user_id')
        risk_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        risk_data = RiskTable.objects.create(
            problem_statement=problem_statement,
            status=status,
            owner=owner,
            message=message,
            eta=eta,
            risk=risk,
            severity=severity,
            impact=impact,
            risk_id=risk_id,
            project=project
        )
        risk_data.save()
        # load risk data to external database
        load_risk_data([(problem_statement, status, owner, message, eta, risk, severity, impact, risk_id, project)])
        return HttpResponseRedirect(reverse("risk"))
    else:
        project = request.session['meta_data'].get('project')
        risk_data = RiskTable.objects.filter(project__in=project)
        return render(request, 'intel_app/risk_table.html', {'data': risk_data, 'project': project})


@csrf_exempt
def key_edit_message(request, pk):
    if request.method == "POST":
        message = request.POST['hiddenInput']
        tab = KeyMessageTable.objects.filter(pk=pk)
        # update the values in external database
        update_key_message_data([(tab[0].message_id, message)])
        # update the values local database
        tab.update(message=message)
        return HttpResponseRedirect(reverse("key_message"))
    else:
        data = KeyMessageTable.objects.filter(pk=pk)
        return render(request, 'intel_app/key_edit_message.html', {'data': data})


@csrf_exempt
def risk_edit_table(request, pk):
    if request.method == "POST":
        ps = request.POST['problem_statement']
        status = request.POST['status']
        owner = request.POST['owner']
        msg = request.POST['message']
        eta = request.POST['eta']
        risk = request.POST['risk']
        severity = request.POST['severity']
        impact = request.POST['impact']

        tab = RiskTable.objects.filter(pk=pk)
        # update the values in external database
        update_risk_data([(ps, status, owner, msg, eta, risk, severity, impact, tab[0].risk_id)])
        # update the values local database
        tab.update(
            problem_statement=ps,
            status=status,
            owner=owner,
            message=msg,
            eta=eta,
            risk=risk,
            severity=severity,
            impact=impact,
        )
        return HttpResponseRedirect(reverse("risk"))
    else:
        risk_data = RiskTable.objects.filter(pk=pk)
        status = ['R', 'G', 'B']
        impact = ['PPA', 'Functionality', 'Quality']
        severity = ['Mgt', '']
        for i in risk_data:
            if i.status in status or i.impact in impact or i.severity in severity:
                # updating the status values
                status.remove(i.status)
                status.insert(0, i.status)
                # updating the impact values
                impact.remove(i.impact)
                impact.insert(0, i.impact)
                # updating the severity values
                severity.remove(i.severity)
                severity.insert(0, i.severity)

        risk_data[0].status = status
        risk_data[0].impact = impact
        risk_data[0].severity = severity
        return render(request, 'intel_app/risk_edit_table.html', {'data': risk_data})


@csrf_exempt
def key_program(request):
    if request.method == "POST":
        category = request.POST['category']
        metric = request.POST['metric']
        print(metric)
        target = request.POST['target']
        print(target)
        actual = request.POST['actual']
        plan = request.POST['plan']
        status = request.POST['status']
        comments = request.POST['comments']
        return HttpResponseRedirect(reverse("key_program"))
    else:
        return render(request, 'intel_app/key_program.html')
