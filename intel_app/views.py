from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

import time
from .models import KeyMessageTable, RiskTable, DetailsMessageTable
from .models import KeyProgramMetricTable, ScheduleMetricTable

from .config import DEFAULT_PASSWORDS

from .db_connection import load_key_message_data
from .db_connection import update_key_message_data
from .db_connection import load_risk_data
from .db_connection import update_risk_data
from .db_connection import load_key_program_metric_data
from .db_connection import update_key_program_metric_data
from .db_connection import delete_key_program_metric_data
from .db_connection import load_details_data
from .db_connection import update_details_data
from .db_connection import load_schedule_data
from .db_connection import update_schedule_data


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
            # risk_data = RiskTable.objects.filter(project__in=project)
            # key_program_data = KeyProgramMetricTable.objects.filter(project__in=project)
            # details_data = DetailsMessageTable.objects.filter(project__in=project)
            # schedule_data = ScheduleMetricTable.objects.filter(project__in=project)
        else:
            key_mess_data = KeyMessageTable.objects.filter(user=user)
            # risk_data = RiskTable.objects.filter(user=user)
            # key_program_data = KeyProgramMetricTable.objects.filter(user=user)
            # details_data = DetailsMessageTable.objects.filter(user=user)
            # schedule_data = ScheduleMetricTable.objects.filter(user=user)

        # get the latest record from the query_set
        if key_mess_data:
            key_mess_data = key_mess_data.latest("created_at")
            if key_mess_data.project in project:
                project.remove(key_mess_data.project)
                project.insert(0, key_mess_data.project)
            key_mess_data.project = project

        # if risk_data:
        #     risk_data = risk_data.latest("created_at")
        #     status = ['R', 'G', 'B', 'Y']
        #     impact = ['PPA', 'Functionality', 'Quality']
        #     severity = ['Mgt', '']
        #     if risk_data.status in status or risk_data.impact in impact or risk_data.severity in severity \
        #             or risk_data.project in project:
        #         # updating the status values
        #         # status.remove(risk_data.status)
        #         # status.insert(0, risk_data.status)
        #         # # updating the impact values
        #         # impact.remove(risk_data.impact)
        #         # impact.insert(0, risk_data.impact)
        #         # # updating the severity values
        #         # severity.remove(risk_data.severity)
        #         # severity.insert(0, risk_data.severity)
        #         # updating the project
        #         project.remove(risk_data.project)
        #         project.insert(0, risk_data.project)
        #     risk_data.status = status
        #     risk_data.impact = impact
        #     risk_data.severity = severity
        #     risk_data.project = project
        #
        # if key_program_data:
        #     key_program_data = key_program_data.latest("created_at")
        #     status = ['R', 'G', 'B', 'Y']
        #     if key_program_data.status in status or key_program_data.project in project:
        #         # updating the status values
        #         # status.remove(key_program_data.status)
        #         # status.insert(0, key_program_data.status)
        #         # # updating the project
        #         project.remove(key_program_data.project)
        #         project.insert(0, key_program_data.project)
        #     key_program_data.status = status
        #     key_program_data.project = project
        #
        # if details_data:
        #     details_data = details_data.latest("created_at")
        #     if details_data.project in project:
        #         project.remove(details_data.project)
        #         project.insert(0, details_data.project)
        #     details_data.project = project
        #
        # if schedule_data:
        #     schedule_data = schedule_data.latest("created_at")
        #     status = ['R', 'G', 'B', 'Y']
        #     #if schedule_data.status in status or schedule_data.project in project:
        #         # updating the status values
        #         # status.remove(schedule_data.status)
        #         # status.insert(0, schedule_data.status)
        #         # # updating the project
        #         # project.remove(schedule_data.project)
        #         # project.insert(0, schedule_data.project)
        #     schedule_data.status = status
        #     schedule_data.project = project

        return render(request, 'intel_app/index.html', {'project': project, 'key_mess_data': key_mess_data,
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
            project='intel',
            user=user
        )
        risk_data.save()
        # load risk data to external database
        #load_risk_data([(problem_statement, status, owner, message, eta, risk, severity, impact, risk_id, project, user)])
        return HttpResponseRedirect(reverse("risk"))
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            if admin:
                risk_data = RiskTable.objects.filter(project__in=project)
            else:
                risk_data = RiskTable.objects.filter(user=user)

            if len(risk_data) >= 1:
                status = ['R', 'G', 'B', 'Y']
                impact = ['PPA', 'Functionality', 'Quality']
                severity = ['Mgt', '']
                for i in risk_data:
                    if i.status in status or i.impact in impact or i.severity in severity \
                            or i.project in project:
                        status.remove(i.status)
                        status.insert(0, i.status)
                        # updating the impact values
                        impact.remove(i.impact)
                        impact.insert(0, i.impact)
                        # updating the severity values
                        severity.remove(i.severity)
                        severity.insert(0, i.severity)
                        i.status = status
                        i.impact = impact
                        i.severity = severity
            return render(request, 'intel_app/risk_table.html', {'data': risk_data, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


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
        print(request.POST)
        tab = RiskTable.objects.filter(pk=pk)
        # update the values in external database
        #update_risk_data([(ps, status, owner, msg, eta, risk, severity, impact, tab[0].risk_id)])
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
        status = ['R', 'G', 'B', 'Y']
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
            category=category,
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
        load_key_program_metric_data([(category, metric, fv_target, current_week_actual,
                                       current_week_plan, status, comments, metric_id, project, user)])
        return HttpResponseRedirect(reverse("key_program"))
    else:
        try:
            project = request.session['meta_data'].get('project')
            metric_data = KeyProgramMetricTable.objects.filter(project__in=project)
            return render(request, 'intel_app/key_program.html', {'data': metric_data, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def key_program_edit(request, pk):
    if request.method == "POST":
        category = request.POST['category']
        metric = request.POST['metric']
        fv_target = request.POST['target']
        current_week_actual = request.POST['actual']
        current_week_plan = request.POST['plan']
        status = request.POST['status']
        comments = request.POST['comments']

        tab = KeyProgramMetricTable.objects.filter(pk=pk)
        # update the values in external database
        update_key_program_metric_data([(category, metric, fv_target, current_week_actual, current_week_plan,
                                         status, comments, tab[0].metric_id)])
        # update the values local database
        tab.update(
            category=category,
            metric=metric,
            fv_target=fv_target,
            current_week_actual=current_week_actual,
            current_week_plan=current_week_plan,
            status=status,
            comments=comments,
        )
        return HttpResponseRedirect(reverse("key_program"))
    else:
        metric_data = KeyProgramMetricTable.objects.filter(pk=pk)
        status = ['R', 'G', 'B', 'Y']
        for i in metric_data:
            if i.status in status:
                # updating the status values
                status.remove(i.status)
                status.insert(0, i.status)

        metric_data[0].status = status
        return render(request, 'intel_app/key_program_edit.html', {'data': metric_data})


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
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            if admin:
                details_mess_data = DetailsMessageTable.objects.filter(project__in=project)
            else:
                details_mess_data = DetailsMessageTable.objects.filter(user=user)
            return render(request, 'intel_app/details.html', {'data': details_mess_data, 'project': project})
        except KeyError:
            return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def details_edit_message(request, pk):
    if request.method == "POST":
        message = request.POST['hiddenInput']
        tab = DetailsMessageTable.objects.filter(pk=pk)
        # update the values in external database
        update_details_data(tab[0].details_id, message)
        # update the values local database
        tab.update(message=message)
        return HttpResponseRedirect(reverse("details"))
    else:
        data = DetailsMessageTable.objects.filter(pk=pk)
        return render(request, 'intel_app/details_edit_message.html', {'data': data})


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
        return HttpResponseRedirect(reverse("home"))
    else:
        try:
            admin = request.session['meta_data'].get('admin')
            project = request.session['meta_data'].get('project')
            user = request.session['meta_data'].get('user_id')
            if admin:
                schedule_data = ScheduleMetricTable.objects.filter(project__in=project)
            else:
                schedule_data = ScheduleMetricTable.objects.filter(user=user)
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
    else:
        metric_data = ScheduleMetricTable.objects.filter(pk=pk)
        status = ['R', 'G', 'B', 'Y']
        for i in metric_data:
            if i.status in status:
                # updating the status values
                status.remove(i.status)
                status.insert(0, i.status)

        metric_data[0].status = status
        return render(request, 'intel_app/schedule_edit_table.html', {'data': metric_data})
