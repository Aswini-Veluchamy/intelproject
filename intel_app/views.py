from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate
from .db_connection import get_data, get_key_msg_or_details_data
import time
from .models import KeyProgramMetricTable

from .config import DEFAULT_PASSWORDS, KEY_PROGRAM_METRIC_TABLE, KEY_MESSAGE_TABLE, LINKS_TABLE
from .config import RISK_TABLE, DETAILS_TABLE, SCHEDULE_TABLE, USER_NAMES

from .db_connection import load_key_message_data
from .db_connection import load_risk_data
from .db_connection import update_risk_data
from .db_connection import load_key_program_metric_data
from .db_connection import update_key_program_metric_data
from .db_connection import delete_key_program_metric_data
from .db_connection import load_details_data
from .db_connection import load_schedule_data
from .db_connection import update_schedule_data
from .db_connection import load_links_data
from .db_connection import update_links_data
from .db_connection import register_user
from .db_connection import login_user
from .db_connection import create_project
from .db_connection import get_projects

import ast

from copy import deepcopy


@csrf_exempt
def user_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # Validating credentials with the database
        if (username in USER_NAMES) and password in DEFAULT_PASSWORDS:
            '''
                if user password matches with default passwords
                render the user to admin page
            '''
            return HttpResponseRedirect(reverse("user_create"))
        else:
            user, data = login_user(username, password)
            if user:
                response = HttpResponseRedirect(reverse('home'))
                response.set_cookie('user_id', data.get('username'))
                response.set_cookie('project', data.get('project'))
                response.set_cookie('admin', data.get('admin'))
                return response
            else:
                context['error'] = "provide valid credentials"
                return render(request, "intel_app/login.html", context)
    else:
        return render(request, "intel_app/login.html")


def user_create(request):
    if request.method == "POST":
        username = request.POST['username']
        project_name = request.POST.getlist('project_name')
        status = request.POST.get('status', 'False')
        password = request.POST['password']
        # registering the user
        register_user(username, password, project_name, bool(status))
        response = HttpResponseRedirect(reverse('login'))
        return response
    else:
        projects = get_projects()
        return render(request, 'intel_app/user_create.html', {'projects': projects})


def project(request):
    if request.method == "POST":
        project = request.POST['project']
        create_project(project)
        return render(request, 'intel_app/project.html')
    else:
        return render(request, 'intel_app/project.html')


def user_logout(request):
    response = HttpResponseRedirect(reverse('login'))
    response.delete_cookie('user_id')
    response.delete_cookie('project')
    response.delete_cookie('admin')
    return response


def forgot_password(request):
    return render(request, 'intel_app/forgot_password.html')


def home(request):
    try:
        project = request.COOKIES['project']
        admin = request.COOKIES['admin']
        user = request.COOKIES['user_id']
        project = ast.literal_eval(project)
        # based on the user filtering the data
        try:
            key_mess_data = get_key_msg_or_details_data(user, KEY_MESSAGE_TABLE)
            if key_mess_data and key_mess_data.get('project') in project:
                project.remove(key_mess_data.get('project'))
                project.insert(0, key_mess_data.get('project'))
                key_mess_data['project'] = project
        except TypeError:
            key_mess_data = None

        try:
            details_data = get_key_msg_or_details_data(user, DETAILS_TABLE)
            if details_data and details_data.get('project') in project:
                project.remove(details_data.get('project'))
                project.insert(0, details_data.get('project'))
                details_data['project'] = project
        except TypeError:
            details_data = None
        return render(request, 'intel_app/index.html', {'project': project,
                                                        'key_mess_data': key_mess_data,
                                                        'details_data': details_data
                                                        })
    except KeyError:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def key_message(request):
    if request.method == "POST":
        message = request.POST['hiddenInput']
        project = request.POST['project']
        user = request.COOKIES['user_id']
        message_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_key_message_data([(message_id, user, message, project)])
        return HttpResponseRedirect(reverse("home"))


@csrf_exempt
def risks(request):
    if request.method == "POST":
        display = request.POST.get('switch_button', 'Off')
        problem_statement = request.POST['problem_statement']
        status = request.POST['status']
        owner = request.POST['owner']
        message = request.POST['message']
        eta = request.POST['eta']
        risk = request.POST['risk']
        severity = request.POST['severity']
        impact = request.POST['impact']
        project = request.POST['project']
        user = request.COOKIES['user_id']
        risk_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        # load risk data to external database
        load_risk_data([
            (problem_statement, status, owner, message, eta, risk, severity, impact, risk_id, project, user, display)
        ])
        return HttpResponseRedirect(reverse("risk"))
    else:
        try:
            project = request.COOKIES['project']
            admin = request.COOKIES['admin']
            user = request.COOKIES['user_id']
            project = ast.literal_eval(project)
            result = get_data(user, RISK_TABLE)
            if result:
                status = ['R', 'G', 'B', 'Y']
                impact = ['PPA', 'Functionality', 'Quality']
                severity = ['None', 'Mgt']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
                    i['severity'] = update_queryset_values(severity, i['severity']) if i['severity'] else severity
                    i['impact'] = update_queryset_values(impact, i['impact'])
            return render(request, 'intel_app/risk_table.html', {'data': result, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def risk_edit_table(request, pk):
    if request.method == "POST":
        print(pk)
        ps = request.POST['problem_statement']
        status = request.POST['status']
        owner = request.POST['owner']
        msg = request.POST['message']
        eta = request.POST['eta']
        risk = request.POST['risk']
        severity = request.POST['severity']
        impact = request.POST['impact']
        if severity == 'None':
            severity = ''
        update_risk_data([(ps, status, owner, msg, eta, risk, severity, impact, pk)])
        return HttpResponseRedirect(reverse("risk"))


@csrf_exempt
def key_program(request):
    if request.method == "POST":
        metric = request.POST['metric']
        fv_target = request.POST['target']
        current_week_actual = request.POST['actual']
        current_week_plan = request.POST['plan']
        status = request.POST['status']
        comments = request.POST['comments']
        project = request.POST['project']

        user = request.COOKIES['user_id']
        metric_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_key_program_metric_data([(metric, fv_target, current_week_actual,
                                       current_week_plan, status, comments, metric_id, project, user)])
        return HttpResponseRedirect(reverse("key_program"))
    else:
        try:
            project = request.COOKIES['project']
            admin = request.COOKIES['admin']
            user = request.COOKIES['user_id']
            project = ast.literal_eval(project)
            result = get_data(user, KEY_PROGRAM_METRIC_TABLE)
            if result:
                status = ['R', 'G', 'B', 'Y']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
            return render(request, 'intel_app/key_program.html', {'data': result, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def key_program_edit(request, pk):
    if request.method == "POST":
        metric = request.POST['metric']
        fv_target = request.POST['target']
        current_week_actual = request.POST['actual']
        current_week_plan = request.POST['plan']
        status = request.POST['status']
        comments = request.POST['comments']
        # update the values in external database
        update_key_program_metric_data([(metric, fv_target, current_week_actual, current_week_plan,
                                        status, comments, pk)])
        return HttpResponseRedirect(reverse("key_program"))


@csrf_exempt
def key_program_delete(request, pk):
    delete_key_program_metric_data(pk)
    return HttpResponseRedirect(reverse("key_program"))


@csrf_exempt
def details(request):
    if request.method == "POST":
        message = request.POST['details_message']
        project = request.POST['details_project']
        user = request.COOKIES['user_id']
        details_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_details_data(details_id, user, message, project)
        return HttpResponseRedirect(reverse("home"))


@csrf_exempt
def schedule(request):
    if request.method == "POST":
        milestone = request.POST['milestone']
        por_commit = request.POST['por_commit']
        por_trend = request.POST['por_trend']
        status = request.POST['status']
        comments = request.POST['comments']
        project = request.POST['project']

        user = request.COOKIES['user_id']
        schedule_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_schedule_data(milestone, por_commit, por_trend, status, comments, schedule_id, user, project)
        return HttpResponseRedirect(reverse("schedule"))
    else:
        try:
            project = request.COOKIES['project']
            admin = request.COOKIES['admin']
            user = request.COOKIES['user_id']
            project = ast.literal_eval(project)
            result = get_data(user, SCHEDULE_TABLE)
            if result:
                status = ['R', 'G', 'B', 'Y']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
            return render(request, 'intel_app/schedule.html', {'data': result, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def schedule_edit_table(request, pk):
    if request.method == "POST":
        milestone = request.POST['milestone']
        por_commit = request.POST['por_commit']
        por_trend = request.POST['por_trend']
        status = request.POST['status']
        comments = request.POST['comments']
        # update the values in external database
        update_schedule_data([(milestone, por_commit, por_trend, status, comments, pk)])
        return HttpResponseRedirect(reverse("schedule"))


def update_queryset_values(data_list: list, input_value: str):
    deep_copy_data = deepcopy(data_list)
    if input_value in deep_copy_data:
        deep_copy_data.remove(input_value)
        deep_copy_data.insert(0, input_value)
    return deep_copy_data


@csrf_exempt
def links(request):
    if request.method == "POST":
        links_url = request.POST['links_url']
        comments = request.POST['comments_links']
        project = request.POST['project']
        user = request.COOKIES['user_id']

        if links_url == '' or comments == '' or project == '':
            raise Exception('fill the fields!!!!!!!!')

        links_id = str(int(time.time() * 1000)) + '_' + user
        load_links_data(links_url, comments, links_id, project, user)
        return HttpResponseRedirect(reverse("links"))
    else:
        project = request.COOKIES['project']
        admin = request.COOKIES['admin']
        user = request.COOKIES['user_id']
        project = ast.literal_eval(project)
        result = get_data(user, LINKS_TABLE)
        return render(request, 'intel_app/links.html', {'project': project, 'data': result})


@csrf_exempt
def links_edit_table(request, pk):
    if request.method == "POST":
        links_url = request.POST['links_url']
        comments = request.POST['comments_links']
        # update the values in external database
        update_links_data(links_url, comments, pk)
        return HttpResponseRedirect(reverse("links"))


@csrf_exempt
def bbox(request):
    if request.method == "POST":
        project = request.POST['project']
        process = request.POST['process']
        die_area = request.POST['die_area']
        config = request.POST['config']
        pv_freq = request.POST['pv_freq']
        perf_target = request.POST['perf_target']
        cdyn = request.POST['cdyn']
        schedule_bbox = request.POST['schedule_bbox']
        print(process)
        return HttpResponseRedirect(reverse("bbox"))
    else:
        project = request.COOKIES['project']
        project = ast.literal_eval(project)
        return render(request, 'intel_app/bbox.html', {'project': project})
