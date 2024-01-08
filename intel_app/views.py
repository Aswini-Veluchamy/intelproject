from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .db_connection import get_data, get_key_message_data
import time
from .models import KeyMessageTable, RiskTable, DetailsMessageTable
from .models import KeyProgramMetricTable, ScheduleMetricTable, LinksMetricTable

from .config import DEFAULT_PASSWORDS

from .db_connection import load_key_message_data
from .db_connection import load_risk_data
from .db_connection import update_risk_data
from .db_connection import load_key_program_metric_data
from .db_connection import update_key_program_metric_data
from .db_connection import delete_key_program_metric_data
from .db_connection import load_details_data
from .db_connection import load_schedule_data
from .db_connection import update_schedule_data

from copy import deepcopy


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
            request.session['meta_data'] = {'user_id': username, 'project': project, 'admin': user.is_superuser}
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
    try:
        project = request.session['meta_data'].get('project')
        admin = request.session['meta_data'].get('admin')
        user = request.session['meta_data'].get('user_id')
        # based on the user filtering the data
        if admin:
            key_mess_data = KeyMessageTable.objects.filter(project__in=project)
            details_data = DetailsMessageTable.objects.filter(project__in=project)
        else:
            key_mess_data = get_key_message_data(user)
            details_data = DetailsMessageTable.objects.filter(user=user)

        if key_mess_data:
            project.remove(key_mess_data.get('project'))
            project.insert(0, key_mess_data.get('project'))
            key_mess_data['project'] = project

        if details_data:
            details_data = details_data.latest("created_at")
            if details_data.project in project:
                project.remove(details_data.project)
                project.insert(0, details_data.project)
            details_data.project = project

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
        user = request.session['meta_data'].get('user_id')
        message_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        key_message_table = KeyMessageTable.objects.create(
            message_id=message_id,
            message=message,
            project=project,
            user=user
        )
        key_message_table.save()
        # load key message to external database
        load_key_message_data([(message_id, user, message, project)])
        return HttpResponseRedirect(reverse("home"))
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            if admin:
                key_mess_data = KeyMessageTable.objects.filter(project__in=project)
            else:
                key_mess_data = KeyMessageTable.objects.filter(user=user)
            return render(request, 'intel_app/key_message.html', {'data': key_mess_data, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


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
            project=project,
            user=user,
            display=display
        )
        risk_data.save()
        # load risk data to external database
        load_risk_data([
            (problem_statement, status, owner, message, eta, risk, severity, impact, risk_id, project, user, display)
        ])
        return HttpResponseRedirect(reverse("risk"))
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            result = get_data(user, 'risk_table')
            print(result)
            if result:
                status = ['R', 'G', 'B', 'Y']
                impact = ['PPA', 'Functionality', 'Quality']
                severity = ['None', 'Mgt']
                for i in result:
                    i['status'] = update_queryset_values(status, i['status'])
                    i['severity'] = update_queryset_values(severity, i['severity']) if i['severity'] else severity
                    i['impact'] = update_queryset_values(impact, i['impact'])
            print("-----------------------------------")
            print(result)
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
        #tab = RiskTable.objects.filter(pk=pk)
        # update the values in external database
        if severity == 'None':
            severity = ''
        update_risk_data([(ps, status, owner, msg, eta, risk, severity, impact, pk)])
        # update the values local database
        # tab.update(
        #     problem_statement=ps,
        #     status=status,
        #     owner=owner,
        #     message=msg,
        #     eta=eta,
        #     risk=risk,
        #     severity=severity,
        #     impact=impact,
        # )
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

        user = request.session['meta_data'].get('user_id')
        metric_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        metric_data = KeyProgramMetricTable.objects.create(
            metric=metric,
            fv_target=fv_target,
            current_week_actual=current_week_actual,
            current_week_plan=current_week_plan,
            status=status,
            comments=comments,
            metric_id=metric_id,
            project=project,
            user=user
        )
        metric_data.save()
        # load key program metric data to external database
        load_key_program_metric_data([(metric, fv_target, current_week_actual,
                                       current_week_plan, status, comments, metric_id, project, user)])
        return HttpResponseRedirect(reverse("key_program"))
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            if admin:
                metric_data = KeyProgramMetricTable.objects.filter(project__in=project)
            else:
                metric_data = KeyProgramMetricTable.objects.filter(user=user)

            if len(metric_data) >= 1:
                status = ['R', 'G', 'B', 'Y']
                for i in metric_data:
                    i.status = update_queryset_values(status, i.status[0])
                    i.save()
            return render(request, 'intel_app/key_program.html', {'data': metric_data, 'project': project})
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

        tab = KeyProgramMetricTable.objects.filter(pk=pk)
        # update the values in external database
        #update_key_program_metric_data([(metric, fv_target, current_week_actual, current_week_plan,
         #                                status, comments, tab[0].metric_id)])
        # update the values local database
        tab.update(
            metric=metric,
            fv_target=fv_target,
            current_week_actual=current_week_actual,
            current_week_plan=current_week_plan,
            status=status,
            comments=comments,
        )
        return HttpResponseRedirect(reverse("key_program"))


@csrf_exempt
def key_program_delete(request, pk):
    tab = KeyProgramMetricTable.objects.filter(pk=pk)
    # delete the data from external database
    delete_key_program_metric_data(tab[0].metric_id)
    # delete the data from local db
    tab.delete()
    return HttpResponseRedirect(reverse("key_program"))


@csrf_exempt
def details(request):
    if request.method == "POST":
        message = request.POST['details_message']
        project = request.POST['details_project']
        user = request.session['meta_data'].get('user_id')
        details_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        details_message_table = DetailsMessageTable.objects.create(
            details_id=details_id,
            message=message,
            project=project,
            user=user
        )
        details_message_table.save()
        # load details data to external database
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

        user = request.session['meta_data'].get('user_id')
        schedule_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        metric_data = ScheduleMetricTable.objects.create(
            milestone=milestone,
            por_commit=por_commit,
            por_trend=por_trend,
            status=status,
            comments=comments,
            schedule_id=schedule_id,
            project=project,
            user=user
        )
        metric_data.save()
        # load schedule metric data to external database
        load_schedule_data(milestone, por_commit, por_trend, status, comments, schedule_id, user, project)
        return HttpResponseRedirect(reverse("schedule"))
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            if admin:
                schedule_data = ScheduleMetricTable.objects.filter(project__in=project)
            else:
                schedule_data = ScheduleMetricTable.objects.filter(user=user)

            if len(schedule_data) >= 1:
                status = ['R', 'G', 'B', 'Y']
                for i in schedule_data:
                    new_status = update_queryset_values(status, i.status[0])
                    i.status = new_status
                    i.save()
            return render(request, 'intel_app/schedule.html', {'data': schedule_data, 'project': project})
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

        tab = ScheduleMetricTable.objects.filter(pk=pk)
        # update the values in external database
        update_schedule_data([(milestone, por_commit, por_trend, status, comments, tab[0].schedule_id)])
        # update the values local database
        tab.update(
            milestone=milestone,
            por_commit=por_commit,
            por_trend=por_trend,
            status=status,
            comments=comments,
        )
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
        user = request.session['meta_data'].get('user_id')

        if links_url == '' or comments == '' or project == '':
            raise Exception('fill the fields!!!!!!!!')

        links_id = str(int(time.time() * 1000)) + '_' + user
        ''' storing data into database'''
        links_data = LinksMetricTable.objects.create(
            links_id=links_id,
            links_url=links_url,
            comments_links=comments,
            project=project,
            user=user
        )
        links_data.save()
        return HttpResponseRedirect(reverse("links"))
    else:
        admin = request.session['meta_data'].get('admin')
        project = request.session['meta_data'].get('project')
        user = request.session['meta_data'].get('user_id')
        if admin:
            links_data = LinksMetricTable.objects.filter(project__in=project)
        else:
            links_data = LinksMetricTable.objects.filter(user=user)
        return render(request, 'intel_app/links.html', {'project': project, 'data': links_data})


@csrf_exempt
def links_edit_table(request, pk):
    if request.method == "POST":
        links_url = request.POST['links_url']
        comments = request.POST['comments_links']
        project = request.POST['project']

        tab = LinksMetricTable.objects.filter(pk=pk)
        # update the values in external database
        #update_schedule_data([(milestone, por_commit, por_trend, status, comments, tab[0].schedule_id)])
        # update the values local database
        tab.update(
            links_url=links_url,
            comments_links=comments,
            project=project,
        )
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
        project = request.session['meta_data'].get('project')

        return render(request, 'intel_app/bbox.html', {'project': project})

def user_create(request):
    if request.method == "POST":
        username = request.POST['username']
        project = request.POST['project']
        password = request.POST['password']
        print(username,password,project)
        return render(request, 'intel_app/user_create.html')
    else:
        return render(request, 'intel_app/user_create.html')