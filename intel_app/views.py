from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import json
import time

from .config import DEFAULT_PASSWORDS, KEY_PROGRAM_METRIC_TABLE, KEY_MESSAGE_TABLE, LINKS_TABLE
from .config import RISK_TABLE, DETAILS_TABLE, SCHEDULE_TABLE, USER_NAMES, ISSUES_TABLE, BBOX_TABLE, LINKS_BKP_TABLE
from .config import ISSUES_BKP_TABLE, RISK_BKP_TABLE, KEY_PROGRAM_METRIC_BKP_TABLE

from .db_connection import load_key_message_data, load_risk_data, update_risk_data, load_details_data
from .db_connection import load_key_program_metric_data, update_key_program_metric_data, delete_key_program_metric_data
from .db_connection import load_schedule_data, update_schedule_data, load_links_data, update_links_data, register_user
from .db_connection import login_user, create_project, get_projects, load_bbox_data, get_projects_data
from .db_connection import update_password, load_issues_data, update_issues_data, get_users, get_users_data, encrypt_password
from .db_connection import get_data, get_key_msg_or_details_data, update_deleted_record, get_bbox_data
from .db_connection import get_record, delete_record, get_schedule_record, update_project, update_project_list, delete_project_from_db

import ast

from copy import deepcopy
from datetime import datetime


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
            try:
                user, data = login_user(username, password)
                projects = ast.literal_eval(data.get('project'))
                primary_project = projects[0]
                if user:
                    response = HttpResponseRedirect(reverse('home'))
                    response.set_cookie('user_id', data.get('username'))
                    response.set_cookie('project', data.get('project'))
                    response.set_cookie('admin', data.get('admin'))
                    response.set_cookie('primary_project', primary_project)
                    return response
                else:
                    context['error'] = "provide valid credentials"
                    return render(request, "intel_app/login.html", context)
            except Exception as e:
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
        # user validation
        users = get_users()
        if users and username in users:
            messages = f'user already exists .....{username}'
        else:
            # registering the user
            encrypt_pwd = encrypt_password(password)
            register_user(username, encrypt_pwd, project_name, bool(status))
            messages = f'user created successfully .....{username}'
        # projects
        projects = get_projects()
        return render(request, 'intel_app/user_create.html', {'projects': projects, 'messages': messages})
    else:
        projects = get_projects()
        return render(request, 'intel_app/user_create.html', {'projects': projects})


def project(request):
    if request.method == "POST":
        project = request.POST['project']
        projects = get_projects()
        if projects and project in projects:
            messages = f'project already exists ......{project}'
            return render(request, 'intel_app/project.html', {'error': messages})
        else:
            create_project(project)
            messages = f'project created successfully ....{project}'
            return HttpResponseRedirect(reverse('project_list'))

    else:
        return render(request, 'intel_app/project.html', {'error': ''})


def user_logout(request):
    # Clear the session data
    request.session.clear()
    response = HttpResponseRedirect(reverse('login'))
    response.delete_cookie('user_id')
    response.delete_cookie('project')
    response.delete_cookie('admin')
    response.delete_cookie('primary_project')
    return response


def forgot_password(request):
    if request.method == "POST":
        username = request.POST['forgot_username']
        password = request.POST['forgot_password']
        ''' updating password'''
        check = update_password(username, password)
        if check:
            message = 'Password updated successfully...'
        else:
            message = 'Provide valid username ....!!!!'
        return render(request, 'intel_app/forgot_password.html', {'messages': message})
    else:
        return render(request, 'intel_app/forgot_password.html')


def home(request):
    try:
        project_data = request.COOKIES['project']
        user = request.COOKIES['user_id']
        user_projects = ast.literal_eval(project_data)
        primary_project = request.COOKIES['primary_project']
        # based on the user filtering the data
        try:
            key_mess_data = get_key_msg_or_details_data(KEY_MESSAGE_TABLE, primary_project)
        except TypeError:
            key_mess_data = None
        try:
            details_data = get_key_msg_or_details_data(DETAILS_TABLE, primary_project)
        except TypeError:
            details_data = None
        # return the data to UI
        return render(request, 'intel_app/index.html', {'project': user_projects,
                                                        'key_mess_data': key_mess_data,
                                                        'details_data': details_data, 'user': user})
    except KeyError:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def key_message(request):
    if request.method == "POST":
        primary_project = request.COOKIES['primary_project']
        message = request.POST['hiddenInput']
        print(message)
        user = request.COOKIES['user_id']
        message_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_key_message_data([(message_id, user, message, primary_project)])
        return HttpResponseRedirect(reverse("home"))
    else:
        try:
            project_data = request.COOKIES['project']
            user = request.COOKIES['user_id']
            user_projects = ast.literal_eval(project_data)
            primary_project = request.COOKIES['primary_project']
            # based on the user filtering the data
            try:
                key_mess_data = get_key_msg_or_details_data(KEY_MESSAGE_TABLE, primary_project)
            except TypeError:
                key_mess_data = None
            # return the data to UI
            return render(request, 'intel_app/key_message.html', {'project': user_projects,
                                                            'key_mess_data': key_mess_data,
                                                            'user': user})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def details(request):
    if request.method == "POST":
        message = request.POST['details_message']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        details_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_details_data(details_id, user, message, primary_project)
        return HttpResponseRedirect(reverse("home"))
    else:
        try:
            project_data = request.COOKIES['project']
            user = request.COOKIES['user_id']
            user_projects = ast.literal_eval(project_data)
            primary_project = request.COOKIES['primary_project']
            # based on the user filtering the data
            try:
                details_data = get_key_msg_or_details_data(DETAILS_TABLE, primary_project)
            except TypeError:
                details_data = None
            # return the data to UI
            return render(request, 'intel_app/details.html', {'project': user_projects,
                                                            'details_data': details_data, 'user': user})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def risks(request):
    if request.method == "POST":
        display = request.POST['switch_button']
        risk_summary = request.POST['risk_summary']
        risk_area = request.POST['risk_area']
        status = request.POST['status']
        owner = request.POST['owner']
        consequence = request.POST['consequence']
        mitigations = request.POST['mitigations']
        trigger_date = request.POST['trigger_date']
        risk_initiated = request.POST['risk_initiated']
        impact = request.POST['impact']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        risk_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        trigger_date = check_por_trend_values(trigger_date)
        risk_initiated = check_por_trend_values(risk_initiated)
        # load risk data to external database
        load_risk_data((display, risk_summary, risk_area, status, owner, consequence, mitigations,
             trigger_date, risk_initiated, impact, risk_id, primary_project, user), RISK_TABLE)

        # load risk data to bkp table
        load_risk_data((display, risk_summary, risk_area, status, owner, consequence, mitigations,
             trigger_date, risk_initiated, impact, risk_id, primary_project, user), RISK_BKP_TABLE)
        return HttpResponseRedirect(reverse("risk"))
    else:
        try:
            user_project = request.COOKIES['project']
            user = request.COOKIES['user_id']
            user_project = ast.literal_eval(user_project)
            result = get_data(user, RISK_TABLE, request.COOKIES['primary_project'])
            if result:
                status = ['Open', 'Closed']
                impact = ['Low', 'Medium', 'High']
                risk_area = ['Cost', 'Schedule', 'Functionality', 'Performance', 'Power', 'Area']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
                    i['impact'] = update_queryset_values(impact, i['impact'])
                    i['risk_area'] = update_queryset_values(risk_area, i['risk_area'])

            return render(request, 'intel_app/risk_table.html', {'data': result, 'project': user_project,
                                                                 'user': user})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def risk_edit_table(request, pk):
    if request.method == "POST":
        print(request.POST)
        display = request.POST['switch_button']
        risk_summary = request.POST['risk_summary']
        risk_area = request.POST['risk_area']
        status = request.POST['status']
        owner = request.POST['owner']
        consequence = request.POST['consequence']
        mitigations = request.POST['mitigations']
        trigger_date = request.POST['trigger_date']
        risk_initiated = request.POST['risk_initiated']
        impact = request.POST['impact']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']

        trigger_date = check_por_trend_values(trigger_date)
        risk_initiated = check_por_trend_values(risk_initiated)
        # updating the project
        update_risk_data([(display, risk_summary, risk_area, status, owner, consequence, mitigations,
                           trigger_date, risk_initiated, impact, pk)])
        # load risk data to bkp table
        load_risk_data((display, risk_summary, risk_area, status, owner, consequence, mitigations,
                        trigger_date, risk_initiated, impact, pk, primary_project, user), RISK_BKP_TABLE)
        return HttpResponseRedirect(reverse("risk"))


@csrf_exempt
def key_program(request):
    if request.method == "POST":
        display = request.POST['switch_button']
        metric = request.POST['metric']
        fv_target = request.POST['target']
        current_week_actual = request.POST['actual']
        current_week_plan = request.POST['plan']
        status = request.POST['status']
        comments = request.POST['comments']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        metric_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        load_key_program_metric_data([(display, metric, fv_target, current_week_actual,
                                       current_week_plan, status, comments, metric_id, primary_project, user)],
                                     KEY_PROGRAM_METRIC_TABLE)
        # backup table
        load_key_program_metric_data([(display, metric, fv_target, current_week_actual,
                                       current_week_plan, status, comments, metric_id, primary_project, user)],
                                     KEY_PROGRAM_METRIC_BKP_TABLE)
        return HttpResponseRedirect(reverse("key_program"))
    else:
        try:
            user_projects = request.COOKIES['project']
            user = request.COOKIES['user_id']
            user_projects = ast.literal_eval(user_projects)
            result = get_data(user, KEY_PROGRAM_METRIC_TABLE,  request.COOKIES['primary_project'])
            if result:
                status = ['R', 'G', 'B', 'Y']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
            return render(request, 'intel_app/key_program.html', {'data': result, 'project': user_projects,
                                                                  'user': user})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def key_program_edit(request, pk):
    if request.method == "POST":
        display = request.POST['switch_button']
        metric = request.POST['metric']
        fv_target = request.POST['target']
        current_week_actual = request.POST['actual']
        current_week_plan = request.POST['plan']
        status = request.POST['status']
        comments = request.POST['comments']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        # update the values in external database
        update_key_program_metric_data([(display, metric, fv_target, current_week_actual, current_week_plan,
                                        status, comments, pk)])

        # backup table
        load_key_program_metric_data([(display, metric, fv_target, current_week_actual,
                                       current_week_plan, status, comments, pk, primary_project, user)],
                                     KEY_PROGRAM_METRIC_BKP_TABLE)
        return HttpResponseRedirect(reverse("key_program"))


@csrf_exempt
def key_program_delete(request, pk):
    delete_key_program_metric_data(pk)
    return HttpResponseRedirect(reverse("key_program"))

@csrf_exempt
def schedule(request):
    if request.method == "POST":
        display = request.POST['switch_button']
        milestone = request.POST['milestone']
        por_commit = request.POST['por_commit']
        por_trend = request.POST['por_trend']
        status = request.POST['status']
        comments = request.POST['comments']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        schedule_id = str(int(time.time() * 1000)) + '_' + user

        # verifying the values
        por_commit = check_por_trend_values(por_commit)
        por_trend = check_por_trend_values(por_trend)

        ''' storing data into database'''
        load_schedule_data(display, milestone, por_commit, por_trend, status, comments, schedule_id, user, primary_project,
                           datetime.now(),
                           False, 'None', datetime.now().date())
        return HttpResponseRedirect(reverse("schedule"))
    else:
        try:
            user_projects = request.COOKIES['project']
            user = request.COOKIES['user_id']
            user_projects = ast.literal_eval(user_projects)
            result = get_data(user, SCHEDULE_TABLE, request.COOKIES['primary_project'], False)
            if result:
                status = ['R', 'G', 'B', 'Y', 'Done']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
            return render(request, 'intel_app/schedule.html', {'data': result, 'project': user_projects,
                                                               'user': user})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


def check_por_trend_values(input_string):
    if '.' not in input_string and input_string:
        return f'{input_string}.5'
    else:
        return input_string


@csrf_exempt
def schedule_edit_table(request, pk):
    if request.method == "POST":
        display = request.POST['switch_button']
        milestone = request.POST['milestone']
        por_commit = request.POST['por_commit']
        por_trend = request.POST['por_trend']
        status = request.POST['status']
        comments = request.POST['comments']
        # update the values in external database
        por_commit = check_por_trend_values(por_commit)
        record = get_schedule_record(pk)
        update_schedule_data([(display, milestone, por_commit, record[0].get('por_commit'), record[0].get('por_trend'),
                               status, comments, pk)])
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
        display = request.POST['switch_button']
        links_url = request.POST['links_url']
        comments = request.POST['comments_links']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']

        if links_url == '' or comments == '' or primary_project == '':
            raise Exception('fill the fields!!!!!!!!')

        links_id = str(int(time.time() * 1000)) + '_' + user
        # original table
        load_links_data(LINKS_TABLE, display, links_url, comments, links_id, primary_project, user)
        # loading backup table
        load_links_data(LINKS_BKP_TABLE, display, links_url, comments, links_id, primary_project, user,
                        False, 'None', datetime.now().date())
        return HttpResponseRedirect(reverse("links"))
    else:
        user_project = request.COOKIES['project']
        user = request.COOKIES['user_id']
        user_project = ast.literal_eval(user_project)
        result = get_data(user, LINKS_TABLE, request.COOKIES['primary_project'])
        return render(request, 'intel_app/links.html', {'project': user_project, 'data': result,
                                                        'user': user})


@csrf_exempt
def links_edit_table(request, pk):
    if request.method == "POST":
        display = request.POST['switch_button']
        links_url = request.POST['links_url']
        comments = request.POST['comments_links']
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        # update the values in external database
        update_links_data(display, links_url, comments, pk)
        # loading backup table
        load_links_data(LINKS_BKP_TABLE, display, links_url, comments, pk, primary_project, user,
                        False, 'None', datetime.now().date())
        return HttpResponseRedirect(reverse("links"))


@csrf_exempt
def bbox(request):
    if request.method == "POST":
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        rows_data = data.get('data', [])
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        load_bbox_data(rows_data, primary_project, user)
        return HttpResponseRedirect(reverse("bbox"))
    else:
        user_projects = request.COOKIES['project']
        user_projects = ast.literal_eval(user_projects)
        user = request.COOKIES['user_id']
        result = get_bbox_data(request.COOKIES['primary_project'])
        count = len(result)
        if count > 1:
            result = sort_data(result)
        return render(request, 'intel_app/bbox.html', {'project': user_projects, 'data': result,
                                                       'user': user, 'count': count})


def sort_data(result):
    data = []
    a = True
    while a:
        for i in result:
            if i['category'] == 'Plan' and len(data) == 0:
                data.insert(0, i)
            elif i['category'] == 'Actual' and len(data) == 1:
                data.insert(1, i)
            elif i['category'] == 'Grading' and len(data) == 2:
                data.insert(2, i)
            elif i['category'] == 'Comments' and len(data) == 3:
                data.insert(3, i)
                a = False
    return data


@csrf_exempt
def bbox_edit(request, pk):
    if request.method == "POST":
        category = request.POST.get('category', '')
        process = request.POST.get('process', '')
        die_area = request.POST.get('die_area', '')
        config = request.POST.get('config', '')
        pv_freq = request.POST.get('pv_freq', '')
        perf_target = request.POST.get('perf_target', '')
        cdyn = request.POST.get('cdyn', '')
        schedule_bbox = request.POST.get('schedule_bbox', '')
        primary_project = request.COOKIES['primary_project']
        user = request.COOKIES['user_id']
        rows_data = [
            {
                'category': category,
                'process': process,
                'die_area': die_area,
                'config': config,
                'pv_freq': pv_freq,
                'perf_target': perf_target,
                'cdyn': cdyn,
                'schedule_bbox': schedule_bbox
            }
        ]
        # update the values in external database
        load_bbox_data(rows_data, primary_project, user)
        return HttpResponseRedirect(reverse("bbox"))


@csrf_exempt
def issues(request):
    if request.method == "POST":
        display = request.POST['switch_button']
        issues_summary = request.POST['issues_summary']
        status = request.POST['status']
        owner = request.POST['owner']
        eta = request.POST['eta']
        trigger_date = request.POST['trigger_date']
        issues_initiated = request.POST['issues_initiated']
        severity = request.POST['severity']
        user = request.COOKIES['user_id']
        primary_project = request.COOKIES['primary_project']
        issues_id = str(int(time.time() * 1000)) + '_' + user

        # verify the values
        trigger_date = check_por_trend_values(trigger_date)
        issues_initiated = check_por_trend_values(issues_initiated)

        ''' storing data into database'''
        # load isuues data to external database
        load_issues_data(ISSUES_TABLE,
                         (display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity,
                          issues_id, primary_project, user)
                         )
        # backup table
        load_issues_data(ISSUES_BKP_TABLE,
            (display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, issues_id,
             primary_project, user, False, 'None', datetime.now().date())
        )
        return HttpResponseRedirect(reverse("issues"))
    else:
        try:
            user_projects = request.COOKIES['project']
            user = request.COOKIES['user_id']
            user_projects = ast.literal_eval(user_projects)
            result = get_data(user, ISSUES_TABLE, request.COOKIES['primary_project'])
            if result:
                status = ['Open', 'Closed']
                severity = ['Low', 'Medium', 'High']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
                    i['severity'] = update_queryset_values(severity, i['severity'])
            return render(request, 'intel_app/issues.html', {'data': result, 'project': user_projects,
                                                             'user': user})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def issues_edit_table(request, pk):
    if request.method == "POST":
        display = request.POST['switch_button']
        issues_summary = request.POST['issues_summary']
        status = request.POST['status']
        owner = request.POST['owner']
        eta = request.POST['eta']
        trigger_date = request.POST['trigger_date']
        issues_initiated = request.POST['issues_initiated']
        severity = request.POST['severity']
        user = request.COOKIES['user_id']
        primary_project = request.COOKIES['primary_project']

        # verify the values
        trigger_date = check_por_trend_values(trigger_date)
        issues_initiated = check_por_trend_values(issues_initiated)

        # updating the table
        update_issues_data([(display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, pk)])
        # backup table
        load_issues_data(ISSUES_BKP_TABLE,
                         (display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity,
                          pk,primary_project, user, False, 'None', datetime.now().date())
                         )
        return HttpResponseRedirect(reverse("issues"))


@csrf_exempt
def project_change(request, func_name):
    response = HttpResponseRedirect(reverse(func_name))
    response.set_cookie('primary_project', request.POST.get('projectdata'))
    return response


def delete_schedule_data(request, pk):
    deleted_by = request.COOKIES['user_id']
    update_deleted_record(SCHEDULE_TABLE, deleted_by, datetime.now().today(), 'schedule_id', pk)
    return HttpResponseRedirect(reverse("schedule"))


def delete_links_data(request, pk):
    deleted_by = request.COOKIES['user_id']
    record = get_record(LINKS_TABLE, 'links_id', pk)
    # loading backup table
    load_links_data(LINKS_BKP_TABLE, record.get('display'), record.get('links_url'), record.get('comments_links'),
                    record.get('links_id'), record.get('project'), record.get('user'),
                    True, deleted_by, datetime.now().date())
    # delete the record
    delete_record(LINKS_TABLE, 'links_id', pk)
    return HttpResponseRedirect(reverse("links"))


def delete_issues_data(request, pk):
    deleted_by = request.COOKIES['user_id']
    record = get_record(ISSUES_TABLE, 'issues_id', pk)
    # loading backup table
    load_issues_data(
        ISSUES_BKP_TABLE, (record['display'], record['issues_summary'], record['status'],
        record['owner'], record['eta'], record['trigger_date'], record['issues_initiated'],
        record['severity'],pk, record['project'], record['user'], True, deleted_by, datetime.now().date())
    )
    # delete the record
    delete_record(ISSUES_TABLE, 'issues_id', pk)
    return HttpResponseRedirect(reverse("issues"))


def user_list(request):
    users = get_users_data()
    projects = get_projects()
    return render(request, 'intel_app/user_list.html', {'users': users, 'projects': projects})


def edit_projects(request):
    # Your view logic here
    if request.method == "POST":
        username = request.POST['username']
        project_name = request.POST.getlist('project_name')
        update_project(username, project_name)
        return HttpResponseRedirect(reverse("user_list"))


def delete_user(request):
    # Your view logic here
    if request.method == "POST":
        username = request.POST['username']
        delete_record('users', 'username', username)
        return HttpResponseRedirect(reverse("user_list"))


def edit_project_list(request, pk):
    if request.method == "POST":
        project_name = request.POST['project_name']
        update_project_list(project_name, pk)
        return HttpResponseRedirect(reverse("project_list"))

def delete_project(request):
    if request.method == "POST":
        project_name = request.POST['project_name']
        delete_project_from_db(project_name)
        return HttpResponseRedirect(reverse("project_list"))


def project_list(request):
    projects = get_projects_data()
    return render(request, 'intel_app/project_list.html', {'projects': projects})


@csrf_exempt
def schedule_data(request):
    try:
        user_projects = request.COOKIES['project']
        user = request.COOKIES['user_id']
        user_projects = ast.literal_eval(user_projects)
        result = get_data(user, SCHEDULE_TABLE, request.COOKIES['primary_project'], False)
        if result:
            status = ['R', 'G', 'B', 'Y', 'Done']
            for i in result:
                i['status'] = update_queryset_values(status, i['status'])
        return render(request, 'intel_app/schedule_data.html', {'data': result, 'project': user_projects,
                                                           'user': user})
    except KeyError:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def schedule_data_edit_table(request, pk):
    if request.method == "POST":
        schedule_comments = request.POST['comments']
        # update the values in external database
        por_commit = check_por_trend_values(por_commit)
        record = get_schedule_record(pk)
        update_schedule_data([(schedule_comments, pk)])
        return HttpResponseRedirect(reverse("schedule_data"))
